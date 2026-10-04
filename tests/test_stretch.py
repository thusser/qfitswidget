import importlib.util
import os
import sys
from pathlib import Path
from types import ModuleType

import numpy as np
import pytest

from qfitswidget.stretch import CUTS_MODES, STRETCH_FUNCTIONS, StretchParams, stretch_to_uint8


def _load_core_stretch() -> ModuleType:
    """pyobs.utils.stretch only needs numpy, but importing the pyobs package pulls in all of pyobs-core, so load
    the file directly: from $PYOBS_CORE (path to a pyobs-core checkout), or a pyobs-core checkout next to this one."""
    root = Path(os.environ.get("PYOBS_CORE", Path(__file__).resolve().parents[2] / "pyobs-core"))
    path = root / "pyobs" / "utils" / "stretch.py"
    if not path.exists():
        pytest.skip(f"pyobs-core not found at {root}, set PYOBS_CORE")
    spec = importlib.util.spec_from_file_location("pyobs_core_stretch", path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module  # dataclasses looks the module up here
    spec.loader.exec_module(module)
    return module


def _frames() -> dict[str, np.ndarray]:
    rng = np.random.default_rng(42)
    return {
        "uint8": rng.integers(0, 256, (300, 400), dtype=np.uint8),
        "uint16": rng.integers(0, 65536, (300, 400), dtype=np.uint16),
        "float32": rng.normal(1000.0, 50.0, (300, 400)).astype(np.float32),
        "rgb": rng.integers(0, 256, (64, 64, 3), dtype=np.uint8),
    }


def test_uint8_default_is_passthrough() -> None:
    data = _frames()["uint8"]
    assert np.array_equal(stretch_to_uint8(data), data)


def test_cuts_follow_source_dtype() -> None:
    # a binned 16 bit frame is float32 by the time it gets here, "full" still means 0..65535
    data = np.full((8, 8), 32768.0, dtype=np.float32)
    out = stretch_to_uint8(data, StretchParams(cuts="full"), dtype="uint16")
    assert np.all(out == 128)


def test_manual_cuts_clip() -> None:
    data = np.array([[0, 50, 100, 150, 200]], dtype=np.uint16)
    out = stretch_to_uint8(data, StretchParams(cuts="manual", lo=50, hi=150))
    assert out.tolist() == [[0, 0, 128, 255, 255]]


def test_full_needs_integer_data() -> None:
    with pytest.raises(ValueError):
        stretch_to_uint8(np.zeros((4, 4), dtype=np.float32), StretchParams(cuts="full"))


def test_invalid_params() -> None:
    with pytest.raises(ValueError):
        StretchParams(stretch="squared")  # type: ignore[arg-type]
    with pytest.raises(ValueError):
        StretchParams(cuts="manual")
    with pytest.raises(ValueError):
        StretchParams(cuts="percentile", lo=90, hi=10)


@pytest.mark.parametrize("name", ["uint8", "uint16", "float32", "rgb"])
@pytest.mark.parametrize("stretch", STRETCH_FUNCTIONS)
@pytest.mark.parametrize("cuts", CUTS_MODES)
def test_matches_pyobs_core(name: str, stretch: str, cuts: str) -> None:
    """The copy must give exactly the same picture as the server side stretch in pyobs-core."""
    core = _load_core_stretch()
    data = _frames()[name]
    kwargs: dict = {"stretch": stretch, "cuts": cuts}
    if cuts == "manual":
        kwargs.update(lo=float(data.min()) + 1, hi=float(data.max()) - 1)
    elif cuts == "percentile":
        kwargs.update(lo=1.0, hi=99.0)
    elif cuts == "full" and not np.issubdtype(data.dtype, np.integer):
        pytest.skip("full needs integer data")
    ours = stretch_to_uint8(data, StretchParams(**kwargs))
    theirs = core.stretch_to_uint8(data, core.StretchParams(**kwargs))
    assert np.array_equal(ours, theirs)

import numpy as np
from astropy.io import fits
from pytestqt.qtbot import QtBot

from qfitswidget import QFitsWidget


def _hdu(dtype: str = "uint16") -> fits.PrimaryHDU:
    rng = np.random.default_rng(1)
    return fits.PrimaryHDU(rng.integers(100, 4000, (120, 160)).astype(dtype))


def test_display_and_presets(qtbot: QtBot) -> None:
    widget = QFitsWidget()
    qtbot.addWidget(widget)
    widget.display(_hdu())
    assert widget.scaled_data is not None
    lo99, hi99 = widget.controls.cut_lo, widget.controls.cut_hi
    assert lo99 < hi99
    assert widget.controls.spinLoCut.isHidden()

    widget.controls.cuts_mode = "95.0%"
    assert widget.controls.cut_lo >= lo99 and widget.controls.cut_hi <= hi99
    assert widget.controls.spinLoCut.isHidden()


def test_custom_cuts_redraw(qtbot: QtBot) -> None:
    widget = QFitsWidget()
    qtbot.addWidget(widget)
    widget.show()
    widget.display(_hdu())
    widget.controls.cuts_mode = "Custom"
    assert not widget.controls.spinLoCut.isHidden()

    # editing the boxes by hand has to redraw with the new cuts
    widget.controls.spinLoCut.setValue(500)
    widget.controls.spinHiCut.setValue(1000)
    assert widget.norm is not None
    assert (widget.norm.vmin, widget.norm.vmax) == (500, 1000)


def test_stretch_and_colormap(qtbot: QtBot) -> None:
    widget = QFitsWidget()
    qtbot.addWidget(widget)
    widget.display(_hdu())
    for stretch in ["linear", "log", "sqrt", "squared", "asinh"]:
        widget.controls.stretch = stretch
        assert widget.scaled_data is not None
    widget.controls.checkColormapReverse.setChecked(True)
    assert widget.cmap == "gray_r"


def test_uint8_disables_cuts_and_stretch(qtbot: QtBot) -> None:
    widget = QFitsWidget()
    qtbot.addWidget(widget)
    widget.display(_hdu("uint8"))
    assert not widget.controls.comboCuts.isEnabled()
    assert not widget.controls.comboStretch.isEnabled()
    assert widget.controls.comboColormap.isEnabled()

from typing import Any, Callable, cast, overload
from matplotlib.colors import Normalize
import numpy as np
import numpy.typing as npt


class FuncNorm(Normalize):  # type: ignore
    """
    Normalize a given value to the 0-1 range on a sqrt scale
    """

    def __init__(self, func: Callable[[float], float], *args: Any, **kwargs: Any):
        Normalize.__init__(self, *args, **kwargs)
        self._func = func

    @overload
    def __call__(self, value: float, clip: bool | None = ...) -> float: ...
    @overload
    def __call__(self, value: np.ndarray, clip: bool | None = ...) -> np.ma.MaskedArray: ...
    @overload
    def __call__(self, value: npt.ArrayLike, clip: bool | None = ...) -> npt.ArrayLike: ...

    def __call__(
        self, value: float | np.ndarray | npt.ArrayLike, clip: bool | None = None
    ) -> float | np.ma.MaskedArray | npt.ArrayLike:
        if clip is None:
            clip = self.clip
        result, is_scalar = self.process_value(value)

        self.autoscale_None(result)
        vmin, vmax = self.vmin, self.vmax
        if vmin is None or vmax is None:
            raise ValueError("vmin and vmax cannot be None")
        if vmin > vmax:
            raise ValueError("minvalue must be less than or equal to maxvalue")
        elif vmin == vmax:
            result.fill(0)
        else:
            if clip:
                mask = np.ma.getmask(result)
                result = np.ma.MaskedArray(np.clip(result.filled(vmax), vmin, vmax), mask=mask)  # type: ignore
            # in-place equivalent of above can be much faster
            resdat = result.data
            mask = result.mask
            if mask is np.ma.nomask:
                mask = resdat <= 0
            else:
                mask |= resdat <= 0
            np.copyto(resdat, 1, where=mask)
            resdat -= self._func(vmin)
            resdat /= self._func(vmax) - self._func(vmin)
            result = np.ma.MaskedArray(resdat, mask=mask, copy=False)  # type: ignore
        if is_scalar:
            result = result[0]
        return result


__all__ = ["FuncNorm"]

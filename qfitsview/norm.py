from matplotlib.colors import Normalize
import numpy as np


class FuncNorm(Normalize):
    """
    Normalize a given value to the 0-1 range on a sqrt scale
    """

    def __init__(self, func, *args, **kwargs):
        Normalize.__init__(self, *args, **kwargs)
        self._func = func

    def __call__(self, value, clip=None):
        if clip is None:
            clip = self.clip
        result, is_scalar = self.process_value(value)
        result = np.ma.masked_less_equal(result, 0, copy=False)

        self.autoscale_None(result)
        vmin, vmax = self.vmin, self.vmax
        if vmin > vmax:
            raise ValueError("minvalue must be less than or equal to maxvalue")
        elif vmin == vmax:
            result.fill(0)
        else:
            if clip:
                mask = np.ma.getmask(result)
                result = np.ma.array(np.clip(result.filled(vmax), vmin, vmax),
                                     mask=mask)
            # in-place equivalent of above can be much faster
            resdat = result.data
            mask = result.mask
            if mask is np.ma.nomask:
                mask = (resdat <= 0)
            else:
                mask |= resdat <= 0
            np.copyto(resdat, 1, where=mask)
            self._func(resdat, resdat)
            resdat -= self._func(vmin)
            resdat /= (self._func(vmax) - self._func(vmin))
            result = np.ma.array(resdat, mask=mask, copy=False)
        if is_scalar:
            result = result[0]
        return result


__all__ = ['FuncNorm']

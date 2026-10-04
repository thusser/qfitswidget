from __future__ import annotations
from typing import Any, Literal

import matplotlib.pyplot as plt
import numpy as np
import numpy.typing as npt
from qtpy import QtCore, QtGui, QtWidgets

from qfitswidget.stretch import StretchParams, stretch_to_uint8
from qfitswidget.stretchcontrols import StretchControls

AUTO_CUTS = "auto"
"""Cuts mode that leaves the cuts to the stretch code (full range for 8 bit, min/max otherwise)."""

_PERCENTILE_DEFAULT = (0.5, 99.5)


def render_image(
    data: npt.NDArray[Any],
    params: StretchParams | None = None,
    source_dtype: str | None = None,
    lut: npt.NDArray[np.uint8] | None = None,
    origin: Literal["lower", "upper"] = "lower",
) -> QtGui.QImage:
    """Stretch a raw frame to 8 bit and turn it into a QImage. Safe to call from a worker thread.

    Args:
        data: Frame, 2D (or 3D with one channel), or 3D with three colour channels as last axis.
        params: How to stretch, defaults if None.
        source_dtype: dtype of the frame before it was e.g. binned, which the cuts follow.
        lut: Colormap as 256x3 uint8 array, applied to 2D frames. Gray if None.
        origin: Whether the first row is the bottom (like in FITS) or the top of the image.

    Returns:
        The image, owning its memory.
    """
    if data.ndim == 3 and data.shape[2] == 1:
        data = data[..., 0]
    img = stretch_to_uint8(data, params, dtype=source_dtype)
    if origin == "lower":
        img = np.flip(img, axis=0)

    if img.ndim == 3:
        if img.shape[2] != 3:
            raise ValueError("Colour images need exactly three channels as last axis.")
        img = np.ascontiguousarray(img)
        fmt = QtGui.QImage.Format.Format_RGB888
    elif lut is not None:
        img = np.ascontiguousarray(lut[img])
        fmt = QtGui.QImage.Format.Format_RGB888
    else:
        img = np.ascontiguousarray(img)
        fmt = QtGui.QImage.Format.Format_Grayscale8

    height, width = img.shape[:2]
    # QImage only references the array, so copy it
    return QtGui.QImage(img.data, width, height, img.strides[0], fmt).copy()


class _RenderSignals(QtCore.QObject):
    finished = QtCore.Signal(int, QtGui.QImage)
    failed = QtCore.Signal(int, str)


class _Render(QtCore.QRunnable):
    def __init__(self, generation: int, *args: Any, **kwargs: Any):
        QtCore.QRunnable.__init__(self)
        self.signals = _RenderSignals()
        self._generation = generation
        self._args = args
        self._kwargs = kwargs

    def run(self) -> None:
        try:
            image = render_image(*self._args, **self._kwargs)
        except Exception as e:
            self.signals.failed.emit(self._generation, str(e))
        else:
            self.signals.finished.emit(self._generation, image)


class _ImageView(QtWidgets.QWidget):
    """Shows an image scaled to fit, keeping its aspect ratio."""

    resized = QtCore.Signal()

    def __init__(self, parent: QtWidgets.QWidget | None = None):
        QtWidgets.QWidget.__init__(self, parent)
        self._image: QtGui.QImage | None = None
        self.setMinimumSize(32, 32)
        self.setSizePolicy(QtWidgets.QSizePolicy.Policy.Expanding, QtWidgets.QSizePolicy.Policy.Expanding)

    @property
    def image(self) -> QtGui.QImage | None:
        return self._image

    def set_image(self, image: QtGui.QImage | None) -> None:
        self._image = image
        self.update()

    def resizeEvent(self, event: QtGui.QResizeEvent) -> None:
        super().resizeEvent(event)
        self.resized.emit()

    def paintEvent(self, event: QtGui.QPaintEvent) -> None:
        painter = QtGui.QPainter(self)
        painter.fillRect(self.rect(), QtGui.QColor("black"))
        if self._image is not None and not self._image.isNull():
            size = self._image.size().scaled(self.size(), QtCore.Qt.AspectRatioMode.KeepAspectRatio)
            target = QtCore.QRect(QtCore.QPoint(0, 0), size)
            target.moveCenter(self.rect().center())
            painter.setRenderHint(QtGui.QPainter.RenderHint.SmoothPixmapTransform)
            painter.drawImage(target, self._image)


class QImageWidget(QtWidgets.QWidget):
    """Shows raw images (any integer or float dtype, e.g. 16 bit camera frames, or RGB) with the same stretch and
    cuts controls as QFitsWidget, but without FITS, WCS or matplotlib, so it is quick enough for a live view.

    Frames are stretched in a worker thread. The newest frame is kept, so changing the stretch re-renders it, and
    while a render is running newer frames replace each other, only the latest one is rendered next.

    For streams that are already stretched on the server (e.g. MJPEG) use display_image() instead and set
    stretch_locally to False: the controls then still work and emit params_changed, but nothing is rendered here.
    """

    params_changed = QtCore.Signal(StretchParams)
    """Emitted when the user changed cuts, stretch or colormap, with the resulting parameters."""

    render_failed = QtCore.Signal(str)
    """Emitted when a frame could not be stretched, with the reason."""

    view_resized = QtCore.Signal()
    """Emitted when the area showing the image changed its size, e.g. to request frames that fit it."""

    def __init__(
        self,
        parent: QtWidgets.QWidget | None = None,
        colormap: bool = False,
        origin: Literal["lower", "upper"] = "lower",
    ):
        """Init new widget.

        Args:
            parent: Parent widget.
            colormap: Whether to offer colormaps, otherwise frames are shown in gray.
            origin: Whether the first row of a frame is the bottom (like FITS and QFitsWidget) or the top.
        """
        QtWidgets.QWidget.__init__(self, parent)
        self.origin: Literal["lower", "upper"] = origin
        self.stretch_locally = True
        self._colormap = colormap

        self._frame: npt.NDArray[Any] | None = None
        self._source_dtype: str | None = None
        self._generation = 0
        self._busy = False
        self._pending = False
        self._pool = QtCore.QThreadPool(self)
        self._pool.setMaxThreadCount(1)

        self.view = _ImageView(self)
        self.controls = StretchControls(
            [AUTO_CUTS, "full", "minmax", "percentile", "manual"],
            ["linear", "sqrt", "asinh", "log"],
            spin_modes=["percentile", "manual"],
            colormap=colormap,
            parent=self,
        )
        self.controls.cuts_mode = AUTO_CUTS
        self.controls.changed.connect(self._controls_changed)
        self.view.resized.connect(self.view_resized)

        layout = QtWidgets.QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        layout.addWidget(self.view, 1)
        layout.addWidget(self.controls)

    # ── parameters ─────────────────────────────────────────────────────────

    @property
    def stretch_params(self) -> StretchParams:
        """Parameters as set in the controls."""
        mode = self.controls.cuts_mode
        has_values = mode in ("percentile", "manual")
        return StretchParams(
            stretch=self.controls.stretch,  # type: ignore[arg-type]
            cuts=None if mode == AUTO_CUTS else mode,  # type: ignore[arg-type]
            lo=self.controls.cut_lo if has_values else None,
            hi=self.controls.cut_hi if has_values else None,
        )

    def set_stretch_params(self, params: StretchParams) -> None:
        """Set the controls, without emitting params_changed or re-rendering."""
        with QtCore.QSignalBlocker(self.controls):
            self.controls.cuts_mode = AUTO_CUTS if params.cuts is None else params.cuts
            self.controls.stretch = params.stretch
            if params.lo is not None and params.hi is not None:
                self.controls.set_cut_values(params.lo, params.hi)

    def _controls_changed(self) -> None:
        # percentiles outside 0..100 (e.g. left over from manual cuts) would be rejected
        if self.controls.cuts_mode == "percentile":
            if not 0 <= self.controls.cut_lo < self.controls.cut_hi <= 100:
                self.controls.set_cut_values(*_PERCENTILE_DEFAULT)
        # an invalid combination (manual with lo >= hi) is not worth rendering while the user is still typing
        try:
            params = self.stretch_params
        except ValueError:
            return
        self.params_changed.emit(params)
        if self.stretch_locally:
            self._render()

    # ── display ────────────────────────────────────────────────────────────

    @property
    def view_size(self) -> QtCore.QSize:
        """Size of the area showing the image, i.e. without the controls."""
        return self.view.size()

    @property
    def frame(self) -> npt.NDArray[Any] | None:
        """The newest raw frame."""
        return self._frame

    def display(self, data: npt.NDArray[Any], source_dtype: str | None = None) -> None:
        """Show a raw frame, stretched with the current controls.

        Args:
            data: Frame, 2D, or 3D with three colour channels as last axis.
            source_dtype: dtype of the frame before it was e.g. binned, which the cuts follow.
        """
        self._frame = data
        self._source_dtype = source_dtype
        self._render()

    def display_image(self, image: QtGui.QImage) -> None:
        """Show an image that is already stretched, e.g. a decoded MJPEG frame."""
        self._frame = None
        self._generation += 1
        self.view.set_image(image)

    def clear(self) -> None:
        self._frame = None
        self._generation += 1
        self.view.set_image(None)

    @property
    def image(self) -> QtGui.QImage | None:
        """The image currently shown."""
        return self.view.image

    def _lut(self) -> npt.NDArray[np.uint8] | None:
        if not self._colormap:
            return None
        name = self.controls.colormap
        if name == "gray":
            return None
        rgba = plt.get_cmap(name)(np.linspace(0, 1, 256))
        return np.asarray(rgba[:, :3] * 255, dtype=np.uint8)

    def _render(self) -> None:
        if self._frame is None:
            return
        if self._busy:
            self._pending = True
            return
        try:
            params = self.stretch_params
        except ValueError:
            return
        self._busy = True
        self._pending = False
        runnable = _Render(
            self._generation,
            self._frame,
            params,
            source_dtype=self._source_dtype,
            lut=self._lut(),
            origin=self.origin,
        )
        runnable.signals.finished.connect(self._render_finished)
        runnable.signals.failed.connect(self._render_failed)
        self._pool.start(runnable)

    def _render_finished(self, generation: int, image: QtGui.QImage) -> None:
        self._busy = False
        # skip results of frames that were cleared or replaced by a ready-made image in the meantime
        if generation == self._generation:
            self.view.set_image(image)
        if self._pending:
            self._render()

    def _render_failed(self, generation: int, message: str) -> None:
        self._busy = False
        if generation == self._generation:
            self.render_failed.emit(message)
        if self._pending:
            self._render()

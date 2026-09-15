from __future__ import annotations
import time
from dataclasses import dataclass
from enum import Enum
from typing import Callable, Any, Protocol
import cv2  # type: ignore
import jinja2
import numpy as np
import numpy.typing as npt
from astropy.coordinates import SkyCoord
from astropy.io import fits
from astropy.wcs import WCS
import astropy.units as u
from qtpy import QtCore, QtWidgets, QtGui  # type: ignore
import matplotlib.pyplot as plt
from astropy.wcs.utils import pixel_to_skycoord
from matplotlib import colors
from matplotlib.artist import Artist
from matplotlib.backend_bases import MouseButton
from matplotlib.cm import ScalarMappable
from matplotlib.colors import Normalize
from matplotlib.image import AxesImage
from matplotlib.lines import Line2D
from matplotlib.patches import FancyArrow, Circle
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.text import Text
from qfitswidget.qt.fitswidget_ui import Ui_FitsWidget
from qfitswidget.navigationtoolbar import NavigationToolbar
from qfitswidget.norm import FuncNorm

plt.style.use("dark_background")


class CenterMarkStyle(Enum):
    FULL_CROSS = "Cross"
    HALF_CROSS = "Half cross"
    CIRCLE = "Circle"


@dataclass
class ProcessMouseHoverResult:
    x: float
    y: float
    value: npt.NDArray[np.floating[Any]]
    mean: float
    maxi: float
    cut: np.ndarray


class ProcessMouseHoverSignals(QtCore.QObject):  # type: ignore
    finished = QtCore.Signal(ProcessMouseHoverResult)


class ProcessMouseHover(QtCore.QRunnable):  # type: ignore
    def __init__(self, fits_widget: QFitsWidget):
        QtCore.QRunnable.__init__(self)
        self.signals = ProcessMouseHoverSignals()
        self.fits_widget = fits_widget
        self.x = fits_widget.mouse_pos[0]
        self.y = fits_widget.mouse_pos[1]
        self.wcs = fits_widget.wcs
        self.data = fits_widget.data

    def run(self) -> None:
        if self.data is None:
            return

        # value
        iy, ix = int(self.y), int(self.x)
        value = self.data[iy, ix, :] if len(self.data.shape) == 3 else np.array([self.data[iy, ix]])

        # mean / max
        if len(self.data.shape) == 2:
            cut = self.data[iy - 10 : iy + 11, ix - 10 : ix + 11]
        else:
            cut = self.data[iy - 10 : iy + 11, ix - 10 : ix + 11, :]

        # calculate and show
        try:
            if any([d == 0 for d in cut.shape]):
                raise ValueError
            mean = np.mean(cut)
            maxi = np.max(cut)
        except ValueError:
            mean, maxi = 0, 0

        # zoom
        cut_normed = self.fits_widget.normalize_data(cut)

        # emit
        self.signals.finished.emit(
            ProcessMouseHoverResult(x=self.x, y=self.y, value=value, mean=mean, maxi=maxi, cut=cut_normed)
        )

        # no idea why, but it's a good idea to sleep a little before we finish
        time.sleep(0.01)


class MenuEntry:
    pass


@dataclass
class MenuHeader(MenuEntry):
    """A header in the menu."""

    text: str


@dataclass
class MenuAction(MenuEntry):
    """A header in the menu."""

    text: str
    callback: Callable[[], tuple[tuple[float, float], WCS]]


class MenuSeparator(MenuEntry):
    pass


class CanNormalize(Protocol):
    def __call__(
        self, value: npt.NDArray[np.floating[Any]], clip: bool | None = None
    ) -> npt.NDArray[np.floating[Any]]: ...


class QFitsWidget(QtWidgets.QWidget, Ui_FitsWidget):  # type: ignore
    """PyQt Widget for displaying FITS images."""

    """Signal emitted when new cuts have been calculated."""
    calculatedCuts = QtCore.Signal(int, int)

    def __init__(self, parent: QtWidgets.QWidget | None = None):
        """Init new widget."""
        QtWidgets.QWidget.__init__(self, parent)
        self.setupUi(self)  # type: ignore

        # store hdu and (scaled) data
        self.hdu: fits.PrimaryHDU | None = None
        self.data: npt.NDArray[np.floating[Any]] | None = None
        self.trimmed_data: npt.NDArray[np.floating[Any]] | None = None
        self.sorted_data: npt.NDArray[np.floating[Any]] | None = None
        self.scaled_data: npt.NDArray[np.floating[Any]] | None = None
        self.pixmap = None
        self.cuts = None
        self.wcs = None
        self.position_angle = None
        self.mirrored = None
        self.mouse_pos = (0.0, 0.0)
        self.mouse_pos_wcs: SkyCoord | None = None
        self.cmap: str | None = None
        self.norm: Normalize | None = None
        self._image_plot: AxesImage | None = None
        self._image_text: Text | None = None
        self._image_cache = None
        self._center_artists: list[Artist] = []
        self._directions_artists: list[Artist] = []
        self._zoom_artist: Artist | None = None

        # options
        self._show_overlay = True
        self._text_overlay_visible = True
        self._text_overlay_color = "white"
        self._center_mark_visible = True
        self._center_mark_color = "red"
        self._center_mark_style = CenterMarkStyle.HALF_CROSS
        self._center_mark_size = 30
        self._directions_visible = True
        self._directions_color = "white"
        self._zoom_visible = True
        self._menu_entries: list[MenuEntry] = []

        # Qt canvas
        self.figure, self.ax = plt.subplots()
        self.ax.axis("off")
        self.canvas = FigureCanvas(self.figure)
        self.tools = NavigationToolbar(self, self.canvas, self.widgetTools, coordinates=False)
        self.widgetCanvas.layout().addWidget(self.canvas)
        self.widgetTools.layout().addWidget(self.tools)

        # mouse
        self.canvas.mpl_connect("motion_notify_event", self._mouse_moved)
        self.canvas.mpl_connect("button_press_event", self._mouse_clicked)
        self.canvas.mpl_connect("draw_event", self._draw_handler)

        # zoom
        self.ax_zoom = self.figure.add_axes((0.8, 0.8, 0.15, 0.15))
        self.ax_zoom.set_aspect("equal")
        self.ax_zoom.patch.set_alpha(0.01)
        self.ax_zoom.axis("off")

        # set cuts -- spinLoCut/spinHiCut only mean anything in "Custom" mode (otherwise disabled
        # and driven by _update_cuts_gui()), so hide them outright otherwise instead of just
        # disabling: dead weight in the toolbar row at any width, not just a responsiveness thing
        self.comboCuts.addItems(["100.0%", "99.9%", "99.0%", "95.0%", "Custom"])
        self.comboCuts.setCurrentText("99.9%")
        self.spinLoCut.setVisible(False)
        self.spinHiCut.setVisible(False)

        # set stretch functions
        self.comboStretch.addItems(["linear", "log", "sqrt", "squared", "asinh"])
        self.comboStretch.setCurrentText("sqrt")

        # set colormaps
        self.comboColormap.addItems(sorted([cm for cm in plt.colormaps() if not cm.endswith("_r")]))
        self.comboColormap.setCurrentText("gray")

        # mouse over update thread pool
        self.mouse_over_thread_pool = QtCore.QThreadPool()
        self.mouse_over_thread_pool.setMaxThreadCount(1)

        # signals
        self.checkTrimSec.stateChanged.connect(self._trim_image)
        self.comboStretch.currentTextChanged.connect(self._draw_image)
        self.comboColormap.currentTextChanged.connect(self._draw_image)
        self.checkColormapReverse.toggled.connect(self._draw_image)
        self.comboCuts.currentTextChanged.connect(self._draw_image)
        self.spinLoCut.valueChanged.connect(self._draw_image)
        self.spinHiCut.valueChanged.connect(self._draw_image)

        # responsive toolbar row (see specs/2026-09-14-fitswidget-toolbar-overflow.md in pyobs-gui,
        # hosted there since this repo has no specs/ of its own): as horizontalLayout_3 runs out of
        # width, first drop the three labels (their text just moves to a tooltip on the combo they
        # described), then push checkTrimSec into an overflow menu, then checkColormapReverse too.
        # Thresholds are measured against this row's own real sizeHint() at each tier (see
        # _measure_toolbar_tier_widths()) rather than hardcoded -- a pixel constant picked once
        # against today's font/DPI/style would silently drift the moment any of those change.
        (
            self._TOOLBAR_HIDE_LABELS_WIDTH,
            self._TOOLBAR_OVERFLOW_TRIMSEC_WIDTH,
            self._TOOLBAR_OVERFLOW_REVERSED_WIDTH,
            self._TOOLBAR_FULLY_COMPACTED_WIDTH,
        ) = self._measure_toolbar_tier_widths()
        self._overflow_menu = QtWidgets.QMenu(self)
        # One QWidgetAction per overflow-able widget, created once and reused for the widget's
        # entire lifetime -- never deleted. Earlier version created a fresh QWidgetAction each
        # time a widget entered overflow and deleteLater()'d it on restore; that crashed for real
        # (not just in theory) once an actual Qt event loop got a chance to process the deferred
        # deletion -- confirmed via a real resize-then-grow-back cycle with app.processEvents()
        # pumped in between, which a same-thread direct resizeEvent() call in isolation never
        # exercises. Reusing one action and only toggling its menu membership sidesteps the whole
        # "does releaseWidget() fully sever ownership before deleteLater() runs" question instead
        # of trying to get the timing right.
        self._overflow_widgets = (self.checkTrimSec, self.checkColormapReverse)
        self._overflow_actions: dict[QtWidgets.QWidget, QtWidgets.QWidgetAction] = {
            widget: QtWidgets.QWidgetAction(self._overflow_menu) for widget in self._overflow_widgets
        }
        self._overflowed: set[QtWidgets.QWidget] = set()
        self.buttonOverflow = QtWidgets.QToolButton(self)
        self.buttonOverflow.setText("⋯")  # horizontal ellipsis -- no icon dependency needed
        self.buttonOverflow.setToolTip("More display options")
        self.buttonOverflow.setPopupMode(QtWidgets.QToolButton.ToolButtonPopupMode.InstantPopup)
        self.buttonOverflow.setMenu(self._overflow_menu)
        self.buttonOverflow.setVisible(False)
        self.horizontalLayout_3.addWidget(self.buttonOverflow)

    def _measure_toolbar_tier_widths(self) -> tuple[int, int, int, int]:
        """Derives the three resizeEvent() thresholds, plus the true fully-compacted floor used
        by minimumSizeHint() (see there), from horizontalLayout_3's own real sizeHint() at each
        tier -- toggles the relevant widgets' visibility, reads sizeHint(), and restores
        everything to fully visible afterward (spinLoCut/spinHiCut's own Custom-mode visibility is
        set separately, right after this runs, and is unaffected either way since this method
        never touches them). Runs once, at construction; the resulting numbers are then fixed for
        the widget's lifetime, same as hardcoded constants would be -- this only replaces where
        they come from, not the resizeEvent logic that uses them.

        Four measurements, not three: the *threshold* for overflowing `reversed` has to be
        measured with `reversed` still visible (that's the width at which it stops fitting), but
        the *floor* minimumSizeHint() reports has to be measured with `reversed` already hidden
        too (the actual smallest this row can ever get) -- conflating these was a real bug, not
        just a naming nitpick: minimumSizeHint() returning the threshold width instead of the
        floor told Qt "this can't get any smaller" at the exact point where `reversed` was still
        visible, so a resizeEvent narrow enough to trigger overflowing it was never delivered at
        all -- confirmed live, not just reasoned about (Tim: "only the trimsec checkbox moves into
        the overflow", every time, no matter how narrow)."""
        layout = self.horizontalLayout_3
        margin = 8  # a little above "exactly fits", so a resize near the boundary doesn't flicker

        full_width = layout.sizeHint().width()

        self.labelCuts.setVisible(False)
        self.labelStretch.setVisible(False)
        self.labelColormap.setVisible(False)
        labels_hidden_width = layout.sizeHint().width()

        self.checkTrimSec.setVisible(False)
        trimsec_hidden_width = layout.sizeHint().width()

        self.checkColormapReverse.setVisible(False)
        reversed_hidden_width = layout.sizeHint().width()

        # restore
        self.labelCuts.setVisible(True)
        self.labelStretch.setVisible(True)
        self.labelColormap.setVisible(True)
        self.checkTrimSec.setVisible(True)
        self.checkColormapReverse.setVisible(True)

        return (
            full_width + margin,
            labels_hidden_width + margin,
            trimsec_hidden_width + margin,
            reversed_hidden_width + margin,
        )

    def minimumSizeHint(self) -> QtCore.QSize:
        """Reports the fully-compacted toolbar width as the floor, not whatever the row's
        *current* (possibly not-yet-compacted) visible state happens to need.

        This matters specifically when QFitsWidget lives inside a resizable QScrollArea (as it
        does in pyobs-gui, via stackedWidgetScroll -> ... -> CameraWidget -> DataDisplayWidget):
        Qt decides whether to actually shrink a widget or just show a scrollbar instead based on
        minimumSizeHint(), *before* ever delivering a resizeEvent with a smaller size. Without
        this override, the default minimumSizeHint() reflects horizontalLayout_3's current
        (uncompacted) children, so the scroll area concludes "this needs ~600px" and a scrollbar
        appears -- resizeEvent() then never actually receives a width small enough to trigger its
        own hide/overflow logic at all, a chicken-and-egg deadlock confirmed the hard way in a
        real embedded run, not just in the isolated headless tests above (which resize this
        widget directly and never hit the deadlock, since nothing there was deciding scroll vs.
        shrink on its behalf).

        Caps at _TOOLBAR_FULLY_COMPACTED_WIDTH specifically, not _TOOLBAR_OVERFLOW_REVERSED_WIDTH
        -- the latter is the *threshold* for overflowing `reversed`, measured with `reversed`
        still visible, not the width once it's ALSO hidden. Using it here told Qt this row could
        never get smaller than the size where `reversed` is still shown, so a resizeEvent narrow
        enough to ever overflow it was never delivered -- a second, one-tier-deeper instance of
        the exact same chicken-and-egg shape as the bug above, confirmed live: `reversed` never
        overflowed no matter how far the window shrank, only `trimsec` ever did."""
        hint = super().minimumSizeHint()
        return QtCore.QSize(min(hint.width(), self._TOOLBAR_FULLY_COMPACTED_WIDTH), hint.height())

    # Gap between a tier's hide threshold and its re-show threshold. Without this, a width
    # sitting right at a boundary -- which happens in practice, not just hypothetically: a live
    # drag delivers resize events a couple pixels apart, and reparenting a widget out of/into the
    # layout can itself trigger a follow-up resize event a few pixels narrower or wider than the
    # one that triggered it -- flips the tier's state on every such event, which is exactly the
    # visible flicker Tim hit testing this for real. Confirmed by tracing a simulated drag: real
    # resize events do land within single-digit pixels of each other near a boundary.
    _HYSTERESIS_MARGIN = 24

    def _tier_active(self, width: int, threshold: int, currently_active: bool) -> bool:
        """Whether a hide/overflow tier should be active at this width, given whether it already
        is -- the threshold to *activate* is `threshold`; to *deactivate* once already active, the
        width has to clear `threshold + _HYSTERESIS_MARGIN`, not just `threshold` again."""
        if currently_active:
            return width < threshold + self._HYSTERESIS_MARGIN
        return width < threshold

    def resizeEvent(self, event: QtGui.QResizeEvent) -> None:
        super().resizeEvent(event)
        # event.size(), not self.width() -- normally identical, but relying on self.width() here
        # made this untestable with a directly-constructed QResizeEvent (self.width() then still
        # reflects whatever the widget's real current size happens to be, not the event's size),
        # and reading directly off the event is the more correct/robust practice regardless
        width = event.size().width()

        labels_hidden = self._tier_active(width, self._TOOLBAR_HIDE_LABELS_WIDTH, not self.labelCuts.isVisible())
        show_labels = not labels_hidden
        self.labelCuts.setVisible(show_labels)
        self.labelStretch.setVisible(show_labels)
        self.labelColormap.setVisible(show_labels)
        self.comboCuts.setToolTip("" if show_labels else "Cuts")
        self.comboStretch.setToolTip("" if show_labels else "Stretch")
        self.comboColormap.setToolTip("" if show_labels else "Colormap")

        # priority order matches specs/2026-09-14-fitswidget-toolbar-overflow.md: trimsec goes to
        # overflow before reversed as width shrinks, and comes back out after it as width grows --
        # each _set_overflow() call is independent and idempotent, order here only matters in that
        # it's what the plan's stated priority actually means in code
        trimsec_overflow = self._tier_active(
            width, self._TOOLBAR_OVERFLOW_TRIMSEC_WIDTH, self.checkTrimSec in self._overflowed
        )
        self._set_overflow(self.checkTrimSec, trimsec_overflow)
        reversed_overflow = self._tier_active(
            width, self._TOOLBAR_OVERFLOW_REVERSED_WIDTH, self.checkColormapReverse in self._overflowed
        )
        self._set_overflow(self.checkColormapReverse, reversed_overflow)

    def _set_overflow(self, widget: QtWidgets.QWidget, overflow: bool) -> None:
        """Moves widget between horizontalLayout_3 and the overflow menu -- the actual widget
        instance either way, not a copy, so its signal connections and state survive the move
        untouched. QWidgetAction.setDefaultWidget() is the standard Qt mechanism for embedding a
        real interactive widget inside a QMenu, rather than a QAction-style static entry.

        The QWidgetAction itself (self._overflow_actions[widget]) is created once, in __init__,
        and reused for the widget's entire lifetime -- never deleted here. An earlier version
        created a fresh QWidgetAction on every overflow and deleteLater()'d it on restore; that
        crashed for real once an actual Qt event loop got a chance to process the deferred
        deletion (confirmed via a real resize-then-grow-back cycle with app.processEvents()
        pumped in between -- a direct, synchronous resizeEvent() call in isolation never exercises
        that timing, which is why the earlier version's own headless test didn't catch it).
        Reusing one action and only toggling its menu membership sidesteps the whole "does
        releaseWidget() fully sever ownership before deleteLater() runs" question instead of
        trying to get that timing right."""
        if overflow == (widget in self._overflowed):
            return
        action = self._overflow_actions[widget]
        if overflow:
            self.horizontalLayout_3.removeWidget(widget)
            action.setDefaultWidget(widget)
            self._overflow_menu.addAction(action)
            self._overflowed.add(widget)
        else:
            self._overflow_menu.removeAction(action)
            action.releaseWidget(widget)
            # setVisible(True) must come AFTER addWidget(), not before: QLayout.addWidget()
            # reparents the widget internally, and Qt's documented behavior is that reparenting
            # always hides a widget as a side effect regardless of a setVisible() call made
            # beforehand -- confirmed the hard way, this order silently left restored widgets
            # invisible even though _overflowed correctly showed them as no longer overflowed.
            self.horizontalLayout_3.addWidget(widget)
            widget.setVisible(True)
            self._overflowed.discard(widget)
        self.buttonOverflow.setVisible(len(self._overflowed) > 0)

    def display(self, hdu: fits.PrimaryHDU) -> None:
        """Display image from given HDU.

        Args:
            hdu: HDU to show image from.
        """

        # store HDU and create WCS
        self.hdu = hdu
        self.wcs = WCS(hdu.header)

        # check
        if self.hdu is None or self.wcs is None:
            return

        # get position angle and check whether image was mirrored
        if (
            "CRPIX1" in self.hdu.header
            and "CRPIX2" in self.hdu.header
            and "CTYPE1" in self.hdu.header
            and self.hdu.header["CTYPE1"]
            and "CTYPE2" in self.hdu.header
            and self.hdu.header["CTYPE2"]
        ):
            cx, cy = self.hdu.header["CRPIX1"], self.hdu.header["CRPIX2"]
            coord = self.wcs.pixel_to_world(cx, cy)
            coord_up = self.wcs.pixel_to_world(cx, cy + 10)
            coord_left = self.wcs.pixel_to_world(cx - 10, cy)
            pa_up = coord.position_angle(coord_up).wrap_at(360 * u.deg)
            pa_left = coord.position_angle(coord_left).wrap_at(360 * u.deg)
            self.position_angle = -pa_up.to(u.deg).value
            self.mirrored = pa_up - pa_left > 0

        # do we have a bayer matrix given?
        if "BAYERPAT" in self.hdu.header or "COLORTYP" in self.hdu.header:
            # check layers
            if len(self.hdu.data.shape) != 2:
                raise ValueError("Invalid data format.")

            # got a bayer pattern
            pattern = self.hdu.header["BAYERPAT" if "BAYERPAT" in self.hdu.header else "COLORTYP"]

            # debayer iamge
            self.data = self._debayer(self.hdu.data, pattern)

        else:
            self.data = self.hdu.data

        # 3D, i.e. color, image?
        if len(self.data.shape) == 3:
            # we need three images of uint8 format
            if self.data.shape[0] != 3 and self.data.shape[2] != 3:
                raise ValueError("Data cubes only supported with three layers, which are interpreted as RGB.")
            if self.data.shape[0] == 3:
                # move axis
                self.data = np.moveaxis(self.data, 0, 2)

        # for INT8 images, we don't need cuts
        is_int8 = self.data.dtype == np.uint8

        # colour image?
        is_color = len(self.data.shape) == 3 and self.data.shape[2] == 3

        # enable GUI elements, only important for first image after start
        self.labelCuts.setEnabled(not is_int8)
        self.comboCuts.setEnabled(not is_int8)
        self.spinLoCut.setEnabled(not is_int8)
        self.spinHiCut.setEnabled(not is_int8)
        self.labelStretch.setEnabled(not is_int8)
        self.comboStretch.setEnabled(not is_int8)
        self.labelColormap.setEnabled(not is_color)
        self.comboColormap.setEnabled(not is_color)
        self.checkColormapReverse.setEnabled(not is_color)
        self.checkTrimSec.setEnabled(True)

        # draw image
        self._trim_image()

    def _draw_handler(self, draw_event: Any) -> None:
        self._image_cache = self.canvas.copy_from_bbox(self.figure.bbox)

    @QtCore.Slot(int)  # type: ignore
    def _trim_image(self) -> None:
        # cut trimsec
        self.trimmed_data = self._trimsec(self.hdu, self.data) if self.checkTrimSec.isChecked() else self.data

        # store flattened and sorted pixels
        self.sorted_data = (
            np.sort(self.trimmed_data[self.trimmed_data > 0].flatten(), kind="stable")
            if self.trimmed_data is not None
            else None
        )

        # draw it
        self._draw_image()

    @QtCore.Slot(str)  # type: ignore
    @QtCore.Slot(int)  # type: ignore
    @QtCore.Slot(float)  # type: ignore
    def _draw_image(self) -> None:
        if self.sorted_data is None:
            return

        # cuts
        self._evaluate_cuts_preset()
        vmin = self.spinLoCut.value()
        vmax = self.spinHiCut.value()

        # get normalization
        stretch = self.comboStretch.currentText()
        if stretch == "linear":
            self.norm = colors.Normalize(vmin=vmin, vmax=vmax, clip=True)
        elif stretch == "log":
            self.norm = colors.LogNorm(vmin=vmin, vmax=vmax, clip=True)
        elif stretch == "sqrt":
            self.norm = FuncNorm(np.sqrt, vmin=vmin, vmax=vmax, clip=True)
        elif stretch == "squared":
            self.norm = colors.PowerNorm(2, vmin=vmin, vmax=vmax, clip=True)
        elif stretch == "asinh":
            self.norm = FuncNorm(np.arcsinh, vmin=vmin, vmax=vmax, clip=True)
        else:
            raise ValueError("Invalid stretch")

        # normalize data
        self.scaled_data = self.normalize_data(self.trimmed_data) if self.trimmed_data is not None else None

        # get name of colormap
        self.cmap = self.comboColormap.currentText()
        if self.checkColormapReverse.isChecked():
            self.cmap += "_r"

        # get colormap
        cm = ScalarMappable(norm=self.norm, cmap=plt.get_cmap(self.cmap))

        # create colorbar image
        colorbar = QtGui.QImage(1, 256, QtGui.QImage.Format.Format_ARGB32)
        for i, f in enumerate(np.linspace(vmin, vmax, 256)):
            rgba = cm.to_rgba(f, bytes=True)
            c = QtGui.QColor(*rgba)
            colorbar.setPixelColor(0, i, c)

        # set colorbar
        self.labelColorbar.setPixmap(QtGui.QPixmap(colorbar))

        # clear axis
        self.ax.cla()
        while len(self.ax.artists) > 0:
            self.ax.artists[0].remove()
        while len(self.figure.artists) > 0:
            self.figure.artists[0].remove()
        while len(self.figure.texts) > 0:
            self.figure.texts[0].remove()
        if self._zoom_artist:
            self._zoom_artist.remove()
            self._zoom_artist = None
            self.ax_zoom.cla()
            self.ax_zoom.axis("off")

        # RGB?
        rgb = len(self.scaled_data.shape) == 3

        # no empty axis?
        if not any([d == 0 for d in self.scaled_data.shape]):
            # plot
            with plt.style.context("dark_background"):
                self._image_plot = self.ax.imshow(
                    self.scaled_data, cmap=None if rgb else self.cmap, interpolation="nearest", origin="lower"
                )
            self.ax.axis("off")
            self.figure.subplots_adjust(0, 0.005, 1, 1)

        # draw
        self.canvas.draw()

        # overlay
        if self._show_overlay:
            if self._center_mark_visible:
                self._draw_center(True)
            if self._directions_visible:
                self._draw_directions(True)
            if self._text_overlay_visible:
                self._draw_text_overlay("", True)
            if self._zoom_visible:
                self._draw_zoom(None, True)

        # blit image
        self.canvas.blit(self.figure.bbox)

    def _draw_text_overlay(self, text: str, initial: bool = False) -> None:
        if initial:
            self._image_text = self.figure.text(
                0.01, 0.98, "", fontsize=10, c=self._text_overlay_color, va="top", animated=True
            )

        # draw text
        if self._image_text is not None:
            self._image_text.set_text(text)
            self.ax.draw_artist(self._image_text)

    def _draw_center(self, initial: bool = False) -> None:
        if initial and self.hdu is not None and self.hdu.header is not None and self.hdu.data is not None:
            # get center position
            if "CRPIX1" in self.hdu.header and "CRPIX2" in self.hdu.header:
                x, y = self.hdu.header["CRPIX1"], self.hdu.header["CRPIX2"]
            else:
                x, y = self.hdu.data.shape[1] // 2, self.hdu.data.shape[0] // 2

            # size
            ms = self._center_mark_size
            ms2 = ms * 2

            # init
            self._center_artists = []

            # (half) cross?
            if self._center_mark_style in [CenterMarkStyle.HALF_CROSS, CenterMarkStyle.FULL_CROSS]:
                # first two lines for half cross
                self._center_artists.append(
                    Line2D([x + ms, x + ms2], [y, y], color=self._center_mark_color, transform=self.ax.transData)
                )
                self._center_artists.append(
                    Line2D([x, x], [y + ms, y + ms2], color=self._center_mark_color, transform=self.ax.transData)
                )

                # full cross?
                if self._center_mark_style == CenterMarkStyle.FULL_CROSS:
                    self._center_artists.append(
                        Line2D([x - ms, x - ms2], [y, y], color=self._center_mark_color, transform=self.ax.transData)
                    )
                    self._center_artists.append(
                        Line2D([x, x], [y - ms, y - ms2], color=self._center_mark_color, transform=self.ax.transData)
                    )

            elif self._center_mark_style == CenterMarkStyle.CIRCLE:
                self._center_artists.append(
                    Circle((x, y), ms, fill=False, color=self._center_mark_color, transform=self.ax.transData)
                )

            # add them
            for a in self._center_artists:
                self.ax.add_artist(a)

        # draw them
        for a in self._center_artists:
            self.ax.draw_artist(a)

    def _draw_directions(self, initial: bool = False) -> None:
        if self.position_angle is None:
            return

        if initial:
            # size and stuff
            length = 20
            text = 35
            x, y = 50, 50
            angle_n = np.radians(self.position_angle)
            self._directions_artists = []

            # N line
            w, h = length * np.sin(angle_n), length * np.cos(angle_n)
            self._directions_artists.append(
                FancyArrow(x, y, w, h, width=0.2, head_width=5, transform=None, color=self._directions_color)
            )

            # draw N text
            w, h = -text * np.sin(angle_n), -text * np.cos(angle_n)
            self._directions_artists.append(
                Text(x - w, y - h, "N", ha="center", va="center", transform=None, c=self._directions_color)
            )

            # E line
            angle_e = angle_n - (np.pi / 2 if self.mirrored else -np.pi / 2)
            w, h = -length * np.sin(angle_e), -length * np.cos(angle_e)
            self._directions_artists.append(
                FancyArrow(x, y, w, h, width=0.2, head_width=5, transform=None, color=self._directions_color)
            )

            # draw E text
            w, h = -text * np.sin(angle_e), -text * np.cos(angle_e)
            self._directions_artists.append(
                Text(x + w, y + h, "E", ha="center", va="center", transform=None, c=self._directions_color)
            )

            # add them
            for a in self._directions_artists:
                self.figure.add_artist(a)

        # draw them
        for a in self._directions_artists:
            self.figure.draw_artist(a)

    def _draw_zoom(self, data: npt.NDArray[np.floating[Any]] | None = None, initial: bool = False) -> None:
        if not self.ax_zoom:
            return

        # no data
        if data is None:
            data = np.zeros((11, 11))

        # RGB?
        rgb = len(data.shape) == 3

        # no empty axis?
        if not any([d == 0 for d in data.shape]):
            # clim?
            vmin, vmax = self._image_plot.get_clim() if self._image_plot is not None else (0, 1)

            # plot
            with plt.style.context("dark_background"):
                self._zoom_artist = self.ax_zoom.imshow(
                    data,
                    cmap=None if rgb else self.cmap,
                    interpolation="nearest",
                    origin="lower",
                    vmin=vmin,
                    vmax=vmax,
                    animated=True,
                )
                self.ax_zoom.draw_artist(self._zoom_artist)

    def normalize_data(self, data: npt.NDArray[np.floating[Any]]) -> npt.NDArray[np.floating[Any]]:
        if self.norm is None:
            raise ValueError("No normalization available")
        # for RGB data, we need to normalize manually, since it's not done by imshow
        if len(data.shape) == 3:
            return np.array([self.norm(data[d, :, :]) / 255.0 for d in range(data.shape[0])])
        else:
            return self.norm(data)

    def _evaluate_cuts_preset(self) -> None:
        """When the cuts preset has changed, calculate the new cuts"""

        # get preset
        preset = self.comboCuts.currentText()
        if preset == "Custom":
            # just enable text boxes
            self.spinLoCut.setEnabled(True)
            self.spinLoCut.setVisible(True)
            self.spinHiCut.setEnabled(True)
            self.spinHiCut.setVisible(True)
            return

        # get percentage
        percent = float(preset[:-1])

        # get number of pixels to discard at both ends
        if self.sorted_data is None:
            return
        n = int(len(self.sorted_data) * (1.0 - (percent / 100.0)))

        # get min/max in cut range
        cut = self.sorted_data[n:-n] if n > 0 else self.sorted_data
        cuts = (np.min(cut), np.max(cut))

        # update gui
        self._update_cuts_gui(*cuts)

    def _update_cuts_gui(self, lo: int, hi: int) -> None:
        """Update current cuts shown in GUI.

        Args:
            lo: Low cut.
            hi: Hight cut.
        """

        # disable signals
        self.spinLoCut.blockSignals(True)
        self.spinHiCut.blockSignals(True)

        # set them and disable+hide text boxes -- only meaningful in "Custom" mode
        self.spinLoCut.setValue(lo)
        self.spinLoCut.setEnabled(False)
        self.spinLoCut.setVisible(False)
        self.spinHiCut.setValue(hi)
        self.spinHiCut.setEnabled(False)
        self.spinHiCut.setVisible(False)

        # enable signals
        self.spinLoCut.blockSignals(True)
        self.spinHiCut.blockSignals(True)

    def _mouse_moved(self, event: Any) -> None:
        """Called, whenever the mouse is moved.

        Args:
            event: MPL event
        """

        # get x/y
        x, y = event.xdata, event.ydata

        # only main axes!
        if event.inaxes != self.ax or x is None or y is None:
            return

        # store position
        self.mouse_pos = (float(x), float(y))

        # convert to RA/Dec and store it
        try:
            self.mouse_pos_wcs = pixel_to_skycoord(x, y, self.wcs)
        except (ValueError, AttributeError):
            self.mouse_pos_wcs = None

        # start in thread
        t = ProcessMouseHover(self)
        t.signals.finished.connect(self._update_mouse_over)
        self.mouse_over_thread_pool.tryStart(t)

    def _format_template(self, template: str) -> str:
        environment = jinja2.Environment()
        environment.filters["hms"] = lambda value: value.to_string(unit=u.hourangle, sep=":", pad=True, precision=1)
        environment.filters["dms"] = lambda value: value.to_string(
            unit=u.degree, sep=":", pad=True, alwayssign=True, precision=1
        )
        tpl = environment.from_string(template)
        return tpl.render(pixel=self.mouse_pos, wcs=self.mouse_pos_wcs)

    def _mouse_clicked(self, event: Any) -> None:
        if event.button is MouseButton.RIGHT:
            # if no menu is set, quit here
            if len(self._menu_entries) == 0:
                return

            # create menu
            menu = QtWidgets.QMenu(self)

            # loop entries
            for entry in self._menu_entries:
                # format text
                text = ""
                if isinstance(entry, MenuHeader) or isinstance(entry, MenuAction):
                    text = self._format_template(entry.text)

                # add entry
                if isinstance(entry, MenuSeparator):
                    menu.addSeparator()
                elif isinstance(entry, MenuHeader):
                    menu.addSection(text)
                elif isinstance(entry, MenuAction):
                    action = QtWidgets.QAction(text, self)
                    action.setData((entry.callback, self.mouse_pos, self.mouse_pos_wcs))
                    menu.addAction(action)

            # connect slot and show menu
            menu.triggered.connect(self._menu_action_clicked)
            menu.exec_(QtGui.QCursor.pos())

    @QtCore.Slot(QtGui.QAction)  # type: ignore
    def _menu_action_clicked(self, action: QtGui.QAction) -> None:
        """Run callback for menu click."""
        callback, pixel, wcs = action.data()
        callback(pixel, wcs)

    @QtCore.Slot(ProcessMouseHoverResult)  # type: ignore
    @QtCore.Slot(float, float, np.ndarray, float, float, np.ndarray)  # type: ignore
    def _update_mouse_over(
        self,
        result: ProcessMouseHoverResult,
    ) -> None:
        # if cached image exists, show it
        if self._image_cache is not None:
            self.canvas.restore_region(self._image_cache)

        if self._show_overlay:
            if self._text_overlay_visible and self.hdu is not None:
                # update text overlay
                text = f"X/Y: {result.x:.1f} / {result.y:.1f}\n"

                # WCS? -- Angle.to_string() can hit astropy's own "invalid value encountered in
                # do_format" RuntimeWarning even for perfectly ordinary, finite coordinates (e.g.
                # exactly 180.0 deg, or values right at a 24h/60m/60s sexagesimal rollover boundary
                # -- reproducible with plain SkyCoord(ra=180*u.deg, ...).ra.to_string(u.hour)).
                # Under pyobs-core's global warnings.filterwarnings("error", category=RuntimeWarning)
                # that becomes a real exception, which would otherwise abort this whole method
                # before the overlay is ever drawn or blitted -- so just drop the WCS line on any
                # formatting failure instead of guessing which coordinate values are "safe"
                if "CTYPE1" in self.hdu.header and self.mouse_pos_wcs is not None:
                    try:
                        if "RA---TAN" in self.hdu.header["CTYPE1"]:
                            text += (
                                f"RA/Dec: {self.mouse_pos_wcs.ra.to_string(u.hour, precision=1)} / "
                                f"{self.mouse_pos_wcs.dec.to_string(precision=1)}\n"
                            )
                        elif "HPLN-TAN" in self.hdu.header["CTYPE1"]:
                            text += (
                                f"Tx/Ty: {self.mouse_pos_wcs.Tx.to_string(precision=1)} / "
                                f"{self.mouse_pos_wcs.Ty.to_string(precision=1)}\n"
                            )
                    except Exception:
                        pass

                # more
                val = ", ".join([f"{v:.1f}" for v in result.value])
                text += f"Pixel value: {val}\n"
                text += f"Area mean/max: {result.mean:.1f} / {result.maxi:.1f}\n"
                self._draw_text_overlay(text)

            if self._center_mark_visible:
                self._draw_center()

            if self._directions_visible:
                self._draw_directions()

            if self._zoom_visible:
                self._draw_zoom(result.cut)

        # draw it
        self.canvas.blit(self.figure.bbox)
        self.canvas.flush_events()

        # draw
        # self.canvas_zoom.draw()

    def _trimsec(
        self, hdu: fits.ImageHDU, data: npt.NDArray[np.floating[Any]] | None = None
    ) -> npt.NDArray[np.floating[Any]]:
        """Trim an image to TRIMSEC.

        Args:
            hdu: HDU to take data from.
            data: If given, take this instead of data from HDU.

        Returns:
            Numpy array with image data.
        """

        # no data?
        if data is None:
            if self.hdu is not None and self.hdu.data is not None:
                data = self.hdu.data.copy()
            else:
                raise ValueError("No data.")

        # keyword not given?
        if "TRIMSEC" not in hdu.header:
            # return whole data
            return data

        # get value of section
        sec = hdu.header["TRIMSEC"]

        # split values
        s = sec[1:-1].split(",")
        x = s[0].split(":")
        y = s[1].split(":")

        # set everything else to NaN
        x0 = int(x[0]) - 1
        x1 = int(x[1])
        y0 = int(y[0]) - 1
        y1 = int(y[1])
        data[:, :x0] = 0
        data[:, x1:] = 0
        data[:y0, :] = 0
        data[y1:, :] = 0

        # return data
        return data

    def _debayer(self, arr: npt.NDArray[np.floating[Any]], pattern: str) -> npt.NDArray[np.floating[Any]]:
        """Debayer an image"""

        # what pattern do we have?
        if pattern == "GBRG":
            return cv2.cvtColor(arr, cv2.COLOR_BayerGB2BGR)

        else:
            raise ValueError("Unknown Bayer pattern.")

    @property
    def show_overlay(self) -> bool:
        return self._show_overlay

    @show_overlay.setter
    def show_overlay(self, show: bool) -> None:
        self._show_overlay = show
        self._draw_image()

    @property
    def center_mark_visible(self) -> bool:
        return self._center_mark_visible

    @center_mark_visible.setter
    def center_mark_visible(self, visible: bool) -> None:
        self._center_mark_visible = visible
        self._draw_image()

    @property
    def center_mark_color(self) -> str:
        return self._center_mark_color

    @center_mark_color.setter
    def center_mark_color(self, color: str) -> None:
        self._center_mark_color = color
        self._draw_image()

    @property
    def center_mark_style(self) -> CenterMarkStyle:
        return self._center_mark_style

    @center_mark_style.setter
    def center_mark_style(self, style: CenterMarkStyle) -> None:
        self._center_mark_style = style
        self._draw_image()

    @property
    def center_mark_size(self) -> int:
        return self._center_mark_size

    @center_mark_size.setter
    def center_mark_size(self, size: int) -> None:
        self._center_mark_size = size
        self._draw_image()

    @property
    def directions_visible(self) -> bool:
        return self._directions_visible

    @directions_visible.setter
    def directions_visible(self, visible: bool) -> None:
        self._directions_visible = visible
        self._draw_image()

    @property
    def directions_color(self) -> str:
        return self._directions_color

    @directions_color.setter
    def directions_color(self, color: str) -> None:
        self._directions_color = color
        self._draw_image()

    @property
    def text_overlay_visible(self) -> bool:
        return self._text_overlay_visible

    @text_overlay_visible.setter
    def text_overlay_visible(self, visible: bool) -> None:
        self._text_overlay_visible = visible
        self._draw_image()

    @property
    def text_overlay_color(self) -> str:
        return self._text_overlay_color

    @text_overlay_color.setter
    def text_overlay_color(self, color: str) -> None:
        self._text_overlay_color = color
        self._draw_image()

    @property
    def zoom_visible(self) -> bool:
        return self._zoom_visible

    @zoom_visible.setter
    def zoom_visible(self, visible: bool) -> None:
        self._zoom_visible = visible
        self._draw_image()

    def set_menu(self, entries: list[MenuEntry]) -> None:
        self._menu_entries = entries

    def clear_menu(self) -> None:
        self._menu_entries.clear()


__all__ = ["QFitsWidget", "MenuAction", "MenuHeader", "MenuSeparator"]

from __future__ import annotations
import time
from dataclasses import dataclass
from enum import Enum
from typing import Optional, List, Tuple
import cv2
import logging
from PyQt5 import QtWidgets, QtCore, QtGui
import numpy as np
from PyQt5.QtCore import pyqtSignal, pyqtSlot, QRunnable
from astropy.coordinates import SkyCoord
from astropy.io import fits
from astropy.wcs import WCS
import astropy.units as u
import matplotlib.pyplot as plt
from astropy.wcs.utils import pixel_to_skycoord
from matplotlib import colors
from matplotlib.cm import ScalarMappable
from matplotlib.lines import Line2D
from matplotlib.patches import FancyArrow, Circle
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.text import Text
from mpl_toolkits.axes_grid1.inset_locator import inset_axes

from qfitswidget.qt.fitswidget import Ui_FitsWidget
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
    coord: SkyCoord
    value: np.nparray
    mean: float
    maxi: float
    cut: np.ndarray


class ProcessMouseHoverSignals(QtCore.QObject):
    finished = pyqtSignal(ProcessMouseHoverResult)


class ProcessMouseHover(QRunnable):
    def __init__(self, fits_widget: QFitsWidget):
        QRunnable.__init__(self)
        self.signals = ProcessMouseHoverSignals()
        self.fits_widget = fits_widget
        self.x = fits_widget.mouse_pos[0]
        self.y = fits_widget.mouse_pos[1]
        self.wcs = fits_widget.wcs
        self.data = fits_widget.data

    def run(self) -> None:
        # convert to RA/Dec and show it
        try:
            coord = pixel_to_skycoord(self.x, self.y, self.wcs)
        except (ValueError, AttributeError):
            coord = None

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
            ProcessMouseHoverResult(x=self.x, y=self.y, coord=coord, value=value, mean=mean, maxi=maxi, cut=cut_normed)
        )

        # no idea why, but it's a good idea to sleep a little before we finish
        time.sleep(0.01)


class QFitsWidget(QtWidgets.QWidget, Ui_FitsWidget):
    """PyQt Widget for displaying FITS images."""

    """Signal emitted when new cuts have been calculated."""
    calculatedCuts = pyqtSignal(int, int)

    def __init__(self, parent: Optional[QtWidgets.QWidget] = None):
        """Init new widget."""
        QtWidgets.QWidget.__init__(self, parent)
        self.setupUi(self)

        # store hdu and (scaled) data
        self.hdu = None
        self.data = None
        self.trimmed_data = None
        self.sorted_data = None
        self.scaled_data = None
        self.pixmap = None
        self.cuts = None
        self.wcs = None
        self.position_angle = None
        self.mirrored = None
        self.mouse_pos = (0, 0)
        self.cmap = None
        self.norm = None
        self._image_plot = None
        self._image_text = None
        self._image_cache = None
        self._center_artists: List[plt.Artist] = []
        self._directions_artists: List[plt.Artist] = []
        self._zoom_artist: Optional[plt.Artist] = None

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

        # Qt canvas
        self.figure, self.ax = plt.subplots()
        self.ax.axis("off")
        self.canvas = FigureCanvas(self.figure)
        self.tools = NavigationToolbar(self, self.canvas, self.widgetTools, coordinates=False)
        self.widgetCanvas.layout().addWidget(self.canvas)
        self.widgetTools.layout().addWidget(self.tools)

        # mouse
        self.canvas.mpl_connect("motion_notify_event", self._mouse_moved)
        self.canvas.mpl_connect("draw_event", self._draw_handler)

        # zoom
        self.ax_zoom = self.figure.add_axes([0.8, 0.8, 0.15, 0.15])
        self.ax_zoom.set_aspect("equal")
        self.ax_zoom.patch.set_alpha(0.01)
        self.ax_zoom.axis("off")

        # set cuts
        self.comboCuts.addItems(["100.0%", "99.9%", "99.0%", "95.0%", "Custom"])
        self.comboCuts.setCurrentText("99.9%")

        # set stretch functions
        self.comboStretch.addItems(["linear", "log", "sqrt", "squared", "asinh"])
        self.comboStretch.setCurrentText("sqrt")

        # set colormaps
        self.comboColormap.addItems(sorted([cm for cm in plt.colormaps() if not cm.endswith("_r")]))
        self.comboColormap.setCurrentText("gray")

        # mouse over update thread pool
        self.mouse_over_thread_pool = QtCore.QThreadPool()
        self.mouse_over_thread_pool.setMaxThreadCount(1)

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

    def _draw_handler(self, draw_event):
        self._image_cache = self.canvas.copy_from_bbox(self.figure.bbox)

    @pyqtSlot(int, name="on_checkTrimSec_stateChanged")
    def _trim_image(self) -> None:
        # cut trimsec
        self.trimmed_data = self._trimsec(self.hdu, self.data) if self.checkTrimSec.isChecked() else self.data

        # store flattened and sorted pixels
        self.sorted_data = np.sort(self.trimmed_data[self.trimmed_data > 0].flatten(), kind="stable")

        # draw it
        self._draw_image()

    @pyqtSlot(str, name="on_comboStretch_currentTextChanged")
    @pyqtSlot(str, name="on_comboColormap_currentTextChanged")
    @pyqtSlot(int, name="on_checkColormapReverse_stateChanged")
    @pyqtSlot(str, name="on_comboCuts_currentTextChanged")
    @pyqtSlot(float, name="on_spinLoCut_valueChanged")
    @pyqtSlot(float, name="on_spinLoCut_valueChanged")
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
        self.scaled_data = self.normalize_data(self.trimmed_data)

        # get name of colormap
        self.cmap = self.comboColormap.currentText()
        if self.checkColormapReverse.isChecked():
            self.cmap += "_r"

        # get colormap
        cm = ScalarMappable(norm=self.norm, cmap=plt.get_cmap(self.cmap))

        # create colorbar image
        colorbar = QtGui.QImage(1, 256, QtGui.QImage.Format_ARGB32)
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
        self._image_text.set_text(text)
        self.ax.draw_artist(self._image_text)

    def _draw_center(self, initial: bool = False) -> None:
        if initial:
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

    def _draw_zoom(self, data: Optional[np.ndarray[float]] = None, initial: bool = False) -> None:
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

    def normalize_data(self, data):
        # for RGB data, we need to normalize manually, since it's not done by imshow
        if len(data.shape) == 3:
            return np.array([self.norm(data[d, :, :]) for d in range(data.shape[0])])
        else:
            return self.norm(data)

    def _evaluate_cuts_preset(self) -> None:
        """When the cuts preset has changed, calculate the new cuts"""

        # get preset
        preset = self.comboCuts.currentText()
        if preset == "Custom":
            # just enable text boxes
            self.spinLoCut.setEnabled(True)
            self.spinHiCut.setEnabled(True)
            return

        # get percentage
        percent = float(preset[:-1])

        # get number of pixels to discard at both ends
        n = int(len(self.sorted_data) * (1.0 - (percent / 100.0)))

        # get min/max in cut range
        cut = self.sorted_data[n:-n] if n > 0 else self.sorted_data
        cuts = (np.min(cut), np.max(cut))

        # update gui
        self._update_cuts_gui(*cuts)

    def _update_cuts_gui(self, lo, hi):
        """Update current cuts shown in GUI.

        Args:
            lo: Low cut.
            hi: Hight cut.
        """

        # disable signals
        self.spinLoCut.blockSignals(True)
        self.spinHiCut.blockSignals(True)

        # set them and disable text boxes
        self.spinLoCut.setValue(lo)
        self.spinLoCut.setEnabled(False)
        self.spinHiCut.setValue(hi)
        self.spinHiCut.setEnabled(False)

        # enable signals
        self.spinLoCut.blockSignals(True)
        self.spinHiCut.blockSignals(True)

    def _mouse_moved(self, event):
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
        self.mouse_pos = (x, y)

        # start in thread
        t = ProcessMouseHover(self)
        t.signals.finished.connect(self._update_mouse_over)
        self.mouse_over_thread_pool.tryStart(t)

    @pyqtSlot(ProcessMouseHoverResult)
    @pyqtSlot(float, float, np.ndarray, float, float, np.ndarray)
    def _update_mouse_over(
        self,
        result: ProcessMouseHoverResult,
    ) -> None:
        # if cached image exists, show it
        if self._image_cache is not None:
            self.canvas.restore_region(self._image_cache)

        if self._show_overlay:
            if self._text_overlay_visible:
                # update text overlay
                text = f"X/Y: {result.x:.1f} / {result.y:.1f}\n"

                # WCS?
                if "CTYPE1" in self.hdu.header:
                    if "RA---TAN" in self.hdu.header["CTYPE1"]:
                        text += (
                            f"RA/Dec: {result.coord.ra.to_string(u.hour, precision=1)} / "
                            f"{result.coord.dec.to_string(precision=1)}\n"
                        )
                    elif "HPLN-TAN" in self.hdu.header["CTYPE1"]:
                        text += (
                            f"Tx/Ty: {result.coord.Tx.to_string(precision=1)} / "
                            f"{result.coord.Ty.to_string(precision=1)}\n"
                        )

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

    def _trimsec(self, hdu, data=None) -> np.ndarray:
        """Trim an image to TRIMSEC.

        Args:
            hdu: HDU to take data from.
            data: If given, take this instead of data from HDU.

        Returns:
            Numpy array with image data.
        """

        # no data?
        if data is None:
            data = self.hdu.data.copy()

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

    def _debayer(self, arr: np.ndarray, pattern: str) -> np.ndarray:
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


__all__ = ["QFitsWidget"]

import time
from typing import Optional
import cv2
from PyQt5 import QtWidgets, QtCore, QtGui
import numpy as np
from PyQt5.QtCore import pyqtSignal, pyqtSlot
from astropy.coordinates import SkyCoord
from astropy.wcs import WCS
import astropy.units as u
import matplotlib.pyplot as plt
from astropy.wcs.utils import pixel_to_skycoord
from matplotlib import colors
from matplotlib.cm import ScalarMappable
from skimage.transform import resize
from matplotlib.backends.backend_qt5 import NavigationToolbar2QT
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas

from .fitswidget import Ui_FitsWidget
from .norm import *

plt.style.use("dark_background")


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
        self.mouse_pos = None

        # Qt canvas
        self.figure, self.ax = plt.subplots()
        self.canvas = FigureCanvas(self.figure)
        self.tools = NavigationToolbar2QT(self.canvas, self.widgetTools, coordinates=False)
        self.widgetCanvas.layout().addWidget(self.canvas)
        self.widgetTools.layout().addWidget(self.tools)

        # mouse
        plt.connect("motion_notify_event", self._mouse_moved)

        # and for zoom
        self.figure_zoom, self.ax_zoom = plt.subplots()
        self.canvas_zoom = FigureCanvas(self.figure_zoom)
        self.widgetZoom.layout().addWidget(self.canvas_zoom)

        # set cuts
        self.comboCuts.addItems(["100.0%", "99.9%", "99.0%", "95.0%", "Custom"])
        self.comboCuts.setCurrentText("99.9%")

        # set stretch functions
        self.comboStretch.addItems(["linear", "log", "sqrt", "squared", "asinh"])
        self.comboStretch.setCurrentText("sqrt")

        # set colormaps
        self.comboColormap.addItems(sorted([cm for cm in plt.colormaps() if not cm.endswith("_r")]))
        self.comboColormap.setCurrentText("gray")

    def display(self, hdu) -> None:
        """Display image from given HDU.

        Args:
            hdu: HDU to show image from.
        """

        # store HDU and create WCS
        self.hdu = hdu
        self.wcs = WCS(hdu.header)

        # get position angle and check whether image was mirrored
        if "PC1_1" in self.hdu.header:
            CD11, CD12 = self.hdu.header["PC1_1"], self.hdu.header["PC1_2"]
            CD21, CD22 = self.hdu.header["PC2_1"], self.hdu.header["PC2_2"]
            self.position_angle = np.degrees(np.arctan2(CD12, CD11))
            self.mirrored = (CD11 * CD22 - CD12 * CD21) < 0
        else:
            self.position_angle = None
            self.mirrored = None

        # do we have a bayer matrix given?
        if "BAYERPAT" in self.hdu.header or "COLORTYP" in self.hdu.header:
            # check layers
            if len(hdu.data.shape) != 2:
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
            norm = colors.Normalize(vmin=vmin, vmax=vmax, clip=True)
        elif stretch == "log":
            norm = colors.LogNorm(vmin=vmin, vmax=vmax, clip=True)
        elif stretch == "sqrt":
            norm = FuncNorm(np.sqrt, vmin=vmin, vmax=vmax, clip=True)
        elif stretch == "squared":
            norm = colors.PowerNorm(2, vmin=vmin, vmax=vmax, clip=True)
        elif stretch == "asinh":
            norm = FuncNorm(np.arcsinh, vmin=vmin, vmax=vmax, clip=True)
        else:
            raise ValueError("Invalid stretch")

        # for RGB data, we need to normalize manually, since it's not done by imshow
        if len(self.trimmed_data.shape) == 3:
            self.scaled_data = np.array([norm(self.trimmed_data[d, :, :]) for d in range(self.trimmed_data.shape[0])])
        else:
            self.scaled_data = self.trimmed_data

        # get name of colormap
        cmap = self.comboColormap.currentText()
        if self.checkColormapReverse.isChecked():
            cmap += "_r"

        # get colormap
        cm = ScalarMappable(norm=norm, cmap=plt.get_cmap(cmap))

        # create colorbar image
        colorbar = QtGui.QImage(1, 256, QtGui.QImage.Format_ARGB32)
        for i, f in enumerate(np.linspace(vmin, vmax, 256)):
            rgba = cm.to_rgba(f, bytes=True)
            c = QtGui.QColor(*rgba)
            colorbar.setPixelColor(0, i, c)

        # set colorbar
        self.labelColorbar.setPixmap(QtGui.QPixmap(colorbar))

        # to qimage
        print("qimage:", time.time())
        qimg = self._create_qimage()
        print("draw:", time.time())

        # draw image
        self._draw(self.ax, self.figure, self.canvas, cmap, norm)
        # self._draw(self.ax_zoom, self.figure_zoom, self.canvas_zoom, cmap, norm)

    def _draw(self, ax, figure, canvas, cmap, norm):
        # clear axis
        ax.cla()

        # RGB?
        rgb = len(self.trimmed_data.shape) == 3

        # plot
        with plt.style.context("dark_background"):
            ax.imshow(self.trimmed_data, cmap=None if rgb else cmap, interpolation="nearest", origin="lower")
        ax.axis("off")
        figure.subplots_adjust(0, 0.005, 1, 1)
        canvas.draw()

    def _create_qimage(self):
        """Create a QImage from the data.
        Returns:
            Processed image.
        """

        # get shape of image
        height, width = self.data.shape[-2:]

        # format
        if len(self.scaled_data.shape) == 2:
            # plain and simple B/W
            format = QtGui.QImage.Format_Indexed8
            bytes_per_line = self.data.shape[1]

        else:
            # 3D, i.e. cube, with colour information
            format = QtGui.QImage.Format_RGB888
            bytes_per_line = self.data.shape[2] * 3

        # for cubes, move axis
        # this is necessary, because in FITS we store three different images, i.e. sth like RRRRRGGGGGBBBBB,
        # but we need RGBRGBRGBRGBRGB
        data = np.moveaxis(self.scaled_data, 0, 2) if len(self.scaled_data.shape) == 3 else self.scaled_data

        # create QImage
        image = QtGui.QImage(data.tobytes(), width, height, bytes_per_line, format)

        # flip and return it
        flipped = image.transformed(QtGui.QTransform().scale(1, -1))
        return flipped

    def _evaluate_cuts_preset(self):
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

        # only main canvas!
        if event.canvas != self.canvas or x is None or y is None:
            return

        # show X/Y
        self.textImageX.setText("%.3f" % x)
        self.textImageY.setText("%.3f" % y)

        # convert to RA/Dec and show it
        try:
            coord = pixel_to_skycoord(x, y, self.wcs)
            self.textWorldRA.setText(coord.ra.to_string(u.hour, sep=":"))
            self.textWorldDec.setText(coord.dec.to_string(sep=":"))
        except ValueError:
            self.textWorldRA.clear()
            self.textWorldDec.clear()

        # get value
        try:
            iy, ix = int(y), int(x)
            value = self.hdu.data[iy, ix]
        except IndexError:
            value = ""
        self.textPixelValue.setText(str(value))

        # mean/max
        try:
            # cut
            if len(self.hdu.data.shape) == 2:
                cut = self.hdu.data[iy - 10 : iy + 11, ix - 10 : ix + 11]
            else:
                cut = self.hdu.data[:, iy - 10 : iy + 11, ix - 10 : ix + 11]

            # calculate and show
            if all([s > 0 for s in cut.shape]):
                self.textAreaMean.setText("%.2f" % np.mean(cut))
                self.textAreaMax.setText("%.2f" % np.max(cut))
            else:
                self.textAreaMean.clear()
                self.textAreaMax.clear()

        except ValueError:
            # outside range
            pass

        # limit zoom
        # self.ax_zoom.set_xlim((x - 10, x + 10))
        # self.ax_zoom.set_ylim((y + 10, y - 10))
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


__all__ = ["QFitsWidget"]

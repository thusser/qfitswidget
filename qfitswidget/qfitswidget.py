from PyQt5 import QtWidgets, QtCore, QtGui
import numpy as np
from astropy.wcs import WCS
import astropy.units as u
import matplotlib.pyplot as plt
from astropy.wcs.utils import pixel_to_skycoord
from matplotlib import colors
from matplotlib.cm import ScalarMappable
from skimage.transform import resize

from .fitswidget import Ui_FitsWidget
from .norm import *


class QFitsWidget(QtWidgets.QWidget, Ui_FitsWidget):
    def __init__(self, parent=None):
        QtWidgets.QWidget.__init__(self, parent)
        self.setupUi(self)

        # mouse
        self.imageView.mouseMoved.connect(self._mouse_moved)

        # set cuts
        self.comboCuts.addItems(['100.0%', '99.9%', '99.0%', '95.0%', 'Custom'])
        self.comboCuts.setCurrentText('99.9%')
        self.comboCuts.currentTextChanged.connect(self._cuts_preset_changed)
        self.spinLoCut.valueChanged.connect(self._cuts_changed)
        self.spinHiCut.valueChanged.connect(self._cuts_changed)

        # set stretch functions
        self.comboStretch.addItems(['linear', 'log', 'sqrt', 'squared', 'asinh'])
        self.comboStretch.setCurrentText('sqrt')
        self.comboStretch.currentTextChanged.connect(self._colormap_changed)

        # set colormaps
        self.comboColormap.addItems(sorted([cm for cm in plt.colormaps() if not cm.endswith('_r')]))
        self.comboColormap.setCurrentText('gray')
        self._colormap_changed()
        self.comboColormap.currentTextChanged.connect(self._colormap_changed)
        self.checkColormapReverse.stateChanged.connect(self._colormap_changed)

        # connect trimsec
        self.checkTrimSec.stateChanged.connect(self._trimsec_changed)

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
        self.updating_cuts = False

    def _apply_cuts(self):
        # get cuts
        c1, c2 = self.cuts

        # scale data
        data = (self.data - c1) / (c2 - c1)

        # trim
        data[data < 0] = 0
        data[data > 1] = 1

        # back to short
        data *= 255
        self.scaled_data = np.int8(data)

        # now we need to re-create the pixmap
        self._create_qimage()

    def _debayer(self, arr: np.ndarray, pattern: str) -> np.ndarray:
        """Debayer an image"""

        # what pattern do we have?
        if pattern == 'GBRG':
            # pattern is:  GB
            #              RG
            R = arr[1::2, 0::2]
            G = arr[0::2, 0::2] // 2 + arr[1::2, 1::2] // 2
            B = arr[0::2, 1::2]

        else:
            raise ValueError('Unknown Bayer pattern.')

        # return rescaled cube
        return np.array([resize(a, arr.shape, anti_aliasing=False) for a in [R, G, B]])

    def _create_qimage(self):
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

        # flip it
        flipped = image.transformed(QtGui.QTransform().scale(1, -1))

        # now we need to display it
        self.imageView.setImage(flipped, self.position_angle, self.mirrored)

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
        if 'TRIMSEC' not in hdu.header:
            # return whole data
            return data

        # get value of section
        sec = hdu.header['TRIMSEC']

        # split values
        s = sec[1:-1].split(',')
        x = s[0].split(':')
        y = s[1].split(':')

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

    def display(self, hdu):
        # check supported formats
        if len(hdu.data.shape) == 2:
            # any 2D image is supported
            pass
        elif len(hdu.data.shape) == 3:
            # we need three images of uint8 format
            if hdu.data.shape[0] != 3:
                raise ValueError('Data cubes only supported with three layers, which are interpreted as RGB.')

        # store HDU and create WCS
        self.hdu = hdu
        self.wcs = WCS(hdu.header)

        # get position angle and check whether image was mirrored
        if 'PC1_1' in self.hdu.header:
            CD11, CD12 = self.hdu.header['PC1_1'], self.hdu.header['PC1_2']
            CD21, CD22 = self.hdu.header['PC2_1'], self.hdu.header['PC2_2']
            self.position_angle = np.degrees(np.arctan2(CD12, CD11))
            self.mirrored = (CD11 * CD22 - CD12 * CD21) < 0
        else:
            self.position_angle = None
            self.mirrored = None

        # do we have a bayer matrix given?
        if 'BAYERPAT' in self.hdu.header or 'COLORTYP' in self.hdu.header:
            # got a bayer pattern
            pattern = self.hdu.header['BAYERPAT' if 'BAYERPAT' in self.hdu.header else 'COLORTYP']

            # debayer iamge
            self.data = self._debayer(self.hdu.data, pattern)

        else:
            # just take data
            self.data = self.hdu.data

        # for INT8 images, we don't need cuts
        is_int8 = self.data.dtype == np.uint8

        # colour image?
        is_color = len(self.data.shape) == 3 and self.data.shape[0] == 3

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

        # apply trimsec
        self._trimsec_changed()

        # update info
        x, y = self.imageView.last_cursor_pos
        self._mouse_moved(x, y)

    def _trimsec_changed(self):
        # cut trimsec
        self.trimmed_data = self._trimsec(self.hdu, self.data) if self.checkTrimSec.isChecked() else self.data

        # store flattened and sorted pixels
        self.sorted_data = np.sort(self.trimmed_data[self.trimmed_data > 0].flatten())

        # image type?
        if self.trimmed_data.dtype == np.uint8:
            # image is scaled image directly
            self.scaled_data = self.trimmed_data.copy()
            self._create_qimage()

        else:
            # apply cuts
            self._cuts_preset_changed(self.comboCuts.currentText())

    def _cuts_preset_changed(self, preset):
        if preset == 'Custom':
            # just enable text boxes
            self.spinLoCut.setEnabled(True)
            self.spinHiCut.setEnabled(True)
            return

        # get percentage
        percent = float(preset[:-1])

        # get number of pixels to discard at both ends
        n = int(len(self.sorted_data) * (1. - (percent / 100.)))

        # get min/max in cut range
        cut = self.sorted_data[n:-n] if n > 0 else self.sorted_data
        cuts = (np.min(cut), np.max(cut))

        # set them and disable text boxes
        self.updating_cuts = True
        self.spinLoCut.setValue(cuts[0])
        self.spinLoCut.setEnabled(False)
        self.spinHiCut.setValue(cuts[1])
        self.spinHiCut.setEnabled(False)
        self.updating_cuts = False
        self._cuts_changed()

    def _cuts_changed(self):
        # updating?
        if self.updating_cuts:
            return

        # get them
        cuts = (self.spinLoCut.value(), self.spinHiCut.value())

        # did they change?
        if self.cuts != cuts:
            # store and apply
            self.cuts = cuts

            # apply them
            self._apply_cuts()

    def _mouse_moved(self, x: float, y: float):
        # show X/Y
        self.textImageX.setText('%.3f' % x)
        self.textImageY.setText('%.3f' % (self.scaled_data.shape[-2] - y,))

        # convert to RA/Dec and show it
        try:
            coord = pixel_to_skycoord(x, y, self.wcs)
            self.textWorldRA.setText(coord.ra.to_string(u.hour, sep=':'))
            self.textWorldDec.setText(coord.dec.to_string(sep=':'))
        except ValueError:
            self.textWorldRA.clear()
            self.textWorldDec.clear()

        # get value
        try:
            iy, ix = self.hdu.data.shape[-2] - int(y), int(x)
            value = self.hdu.data[iy, ix]
        except IndexError:
            value = ''
        self.textPixelValue.setText(str(value))

        # mean/max
        try:
            # cut
            if len(self.hdu.data.shape) == 2:
                cut = self.hdu.data[iy - 10:iy + 11, ix - 10: ix + 11]
            else:
                cut = self.hdu.data[:, iy - 10:iy + 11, ix - 10: ix + 11]

            # calculate and show
            if all([s > 0 for s in cut.shape]):
                self.textAreaMean.setText('%.2f' % np.mean(cut))
                self.textAreaMax.setText('%.2f' % np.max(cut))
            else:
                self.textAreaMean.clear()
                self.textAreaMax.clear()

        except ValueError:
            # outside range
            pass

        # get zoom in and scale it to 100x100
        pix = self.imageView.cut(x, y, 10).scaled(101, 101)

        # draw central pixel
        painter = QtGui.QPainter(pix)
        painter.setPen(QtGui.QPen(QtCore.Qt.white, 1))
        painter.drawRect(48, 48, 4, 4)
        painter.setPen(QtGui.QPen(QtCore.Qt.black, 1))
        painter.drawRect(47, 47, 6, 6)
        painter.end()

        # show zoom
        self.labelZoom.setPixmap(pix)

        # get data in zoom
        x, y = int(x), int(y)

    def _colormap_changed(self):
        # get name of colormap
        name = self.comboColormap.currentText()
        if self.checkColormapReverse.isChecked():
            name += '_r'

        # get normalization
        stretch = self.comboStretch.currentText()
        if stretch == 'linear':
            norm = colors.Normalize(vmin=0, vmax=250)
        elif stretch == 'log':
            norm = colors.LogNorm(vmin=0.1, vmax=250)
        elif stretch == 'sqrt':
            norm = FuncNorm(np.sqrt, vmin=0, vmax=250)
        elif stretch == 'squared':
            norm = colors.PowerNorm(2, vmin=0, vmax=250)
        elif stretch == 'asinh':
            norm = FuncNorm(np.arcsinh, vmin=0, vmax=250)
        else:
            raise ValueError('Invalid stretch')

        # get colormap
        cm = ScalarMappable(norm=norm, cmap=plt.get_cmap(name))

        # set it
        self.imageView.setColormap(cm)

        # create colorbar image
        colorbar = QtGui.QImage(1, 256, QtGui.QImage.Format_ARGB32)
        for i in range(256):
            rgba = cm.to_rgba(i, bytes=True)
            c = QtGui.QColor(*rgba)
            colorbar.setPixelColor(0, i, c)

        # set colorbar
        self.labelColorbar.setPixmap(QtGui.QPixmap(colorbar))


__all__ = ['QFitsWidget']

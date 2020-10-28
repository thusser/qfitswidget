from PyQt5 import QtWidgets, QtCore, QtGui
import numpy as np
from astropy.wcs import WCS
import astropy.units as u
import matplotlib.pyplot as plt
from astropy.wcs.utils import pixel_to_skycoord
from matplotlib import colors
from matplotlib.cm import ScalarMappable

from .fitsview import Ui_FitsView
from .norm import *


class QFitsView(QtWidgets.QWidget, Ui_FitsView):
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
        self.sorted_data = None
        self.scaled_data = None
        self.pixmap = None
        self.cuts = None
        self.wcs = None
        self.position_angle = None
        self.mirrored = None

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

    def _create_qimage(self):
        # get shape of data
        height, width = self.scaled_data.shape

        # create QImage
        image = QtGui.QImage(self.scaled_data, width, height, width, QtGui.QImage.Format_Indexed8)

        # flip it
        flipped = image.transformed(QtGui.QTransform().scale(1, -1))

        # now we need to display it
        self.imageView.setImage(flipped, self.position_angle, self.mirrored)

    def _trimsec(self, hdu) -> np.ndarray:
        """Trim an image to TRIMSEC.

        Args:
            hdu: HDU to take data from.

        Returns:
            Numpy array with image data.
        """

        # keyword not given?
        if 'TRIMSEC' not in hdu.header:
            # return whole data
            return hdu.data

        # get value of section
        sec = hdu.header['TRIMSEC']

        # copy data
        data = hdu.data.copy()

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
        # store HDU and create WCS
        self.hdu = hdu
        self.wcs = WCS(hdu.header)

        # get position angle and check whether image was mirrored
        if 'PC1_1' in self.hdu.header:
            CD11, CD12 = self.hdu.header['PC1_1'], self.hdu.header['PC1_2']
            CD21, CD22 = self.hdu.header['PC2_1'], self.hdu.header['PC2_2']
            self.position_angle = np.degrees(np.arctan2(CD12, CD11))
            self.mirrored = (CD11 * CD22 - CD12 * CD21) < 0
            print(self.mirrored)
        else:
            self.position_angle = None
            self.mirrored = None

        # enable GUI elements, only important for first image after start
        self.comboCuts.setEnabled(True)
        self.spinLoCut.setEnabled(True)
        self.spinHiCut.setEnabled(True)
        self.comboStretch.setEnabled(True)
        self.comboColormap.setEnabled(True)
        self.checkColormapReverse.setEnabled(True)
        self.checkTrimSec.setEnabled(True)

        # apply trimsec
        self._trimsec_changed()

    def _trimsec_changed(self):
        # cut trimsec
        self.data = self._trimsec(self.hdu) if self.checkTrimSec.isChecked() else self.hdu.data

        # store flattened and sorted pixels
        self.sorted_data = np.sort(self.data[self.data > 0].flatten())

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
        self.spinLoCut.setValue(cuts[0])
        self.spinLoCut.setEnabled(False)
        self.spinHiCut.setValue(cuts[1])
        self.spinHiCut.setEnabled(False)

    def _cuts_changed(self):
        # get cuts
        self.cuts = (self.spinLoCut.value(), self.spinHiCut.value())

        # apply them
        self._apply_cuts()

    def _mouse_moved(self, x: float, y: float):
        # show X/Y
        self.textImageX.setText('%.3f' % x)
        self.textImageY.setText('%.3f' % (self.scaled_data.shape[0] - y,))

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
            iy, ix = self.hdu.data.shape[0] - int(y), int(x)
            value = self.hdu.data[iy, ix]
        except IndexError:
            value = ''
        self.textPixelValue.setText(str(value))

        # mean/max
        try:
            cut = self.hdu.data[iy - 10:iy + 11, ix - 10: ix + 11]
            self.textAreaMean.setText('%.2f' % np.mean(cut))
            self.textAreaMax.setText('%.2f' % np.max(cut))
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


__all__ = ['QFitsView']

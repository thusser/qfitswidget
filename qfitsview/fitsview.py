from PyQt5 import QtWidgets, QtCore, QtGui
import numpy as np
from astropy.wcs import WCS
import astropy.units as u
import matplotlib.pyplot as plt
from matplotlib import colors
from matplotlib.cm import ScalarMappable


class QImageView(QtWidgets.QWidget):
    mouseMoved = QtCore.pyqtSignal(float, float)

    def __init__(self, *args, **kwargs):
        QtWidgets.QWidget.__init__(self, *args, **kwargs)
        self._image = None
        self._scaled_pixmap = None
        self._image_rect = None
        self._colormap = None

        # set mouse cursor and grab it
        self.setMouseTracking(True)
        self.setCursor(QtCore.Qt.CrossCursor)

        # init colormap
        self.setColormap('gray')

    def setImage(self, image: QtGui.QImage) -> None:
        # set the image
        self._image = image

        # update image
        self._update_image()

    def setColormap(self, name: str) -> None:
        # colormap
        cm = ScalarMappable(norm=colors.Normalize(vmin=0, vmax=255), cmap=plt.get_cmap(name))

        # create colormap and set it
        self._colormap = [QtGui.qRgb(*cm.to_rgba(i, bytes=True)[:3]) for i in range(256)]

        # update image
        self._update_image()

    def _update_image(self):
        # do we have an image?
        if self._image is None:
            return

        # set colormap
        self._image.setColorTable(self._colormap)

        # scale image
        self._scale_image()

        # show it
        self.update()

    def _scale_image(self):
        # do we have an image?
        if self._image is None:
            return

        # get pixmap
        pixmap = QtGui.QPixmap(self._image)

        # resize pixmap to my own size keeping aspect ratio
        w, h = self.width(), self.height()
        self._scaled_pixmap = pixmap.scaled(w, h, QtCore.Qt.KeepAspectRatio)

    def resizeEvent(self, event: QtGui.QResizeEvent) -> None:
        # on resize, resize the pixmap
        self._scale_image()

    def paintEvent(self, a0: QtGui.QPaintEvent) -> None:
        # init painter with black background
        painter = QtGui.QPainter(self)
        painter.setBackground(QtCore.Qt.black)

        # no image?
        if self._scaled_pixmap is None:
            return

        # get x/y coordinates to draw image in centre
        w, h = self.width(), self.height()
        pw, ph = self._scaled_pixmap.width(), self._scaled_pixmap.height()
        x, y = (w - pw) / 2., (h - ph) / 2.

        # draw image
        painter.drawPixmap(x, y, self._scaled_pixmap)

        # remember rect
        self._image_rect = (x, y, pw, ph)

    def cut(self, x: float, y: float, size: int = 5):
        # extract region
        x, y = int(x), int(y)
        return QtGui.QPixmap(self._image.copy(x - size, y - size, size * 2, size * 2))

    def mouseMoveEvent(self, event: QtGui.QMouseEvent) -> None:
        if self._image_rect is None:
            return

        # calculate coordinates in image coordinates
        x = (event.x() - self._image_rect[0]) / self._image_rect[2]
        y = (event.y() - self._image_rect[1]) / self._image_rect[3]

        # trim to 0..1
        x, y = min(max(x, 0), 1),  min(max(y, 0), 1)

        # scale to full image size
        xi, yi = x * self._image.width(), y * self._image.height()

        # emit signal and accept
        self.mouseMoved.emit(xi, yi)
        event.accept()


class QFitsView(QtWidgets.QWidget):
    def __init__(self, parent=None):
        QtWidgets.QWidget.__init__(self, parent)

        # group containing info
        self.groupInfo = QtWidgets.QGroupBox()
        layout = QtWidgets.QGridLayout()
        self.groupInfo.setLayout(layout)

        # image coordinates
        layout.addWidget(QtWidgets.QLabel('Image'), 0, 0)
        layout.addWidget(QtWidgets.QLabel('X:'), 0, 1)
        self.textImageX = QtWidgets.QLineEdit()
        self.textImageX.setReadOnly(True)
        self.textImageX.setAlignment(QtCore.Qt.AlignHCenter)
        layout.addWidget(self.textImageX, 0, 2)
        layout.addWidget(QtWidgets.QLabel('Y:'), 0, 3)
        self.textImageY = QtWidgets.QLineEdit()
        self.textImageY.setReadOnly(True)
        self.textImageY.setAlignment(QtCore.Qt.AlignHCenter)
        layout.addWidget(self.textImageY, 0, 4)
        layout.addWidget(QtWidgets.QLabel('Value:'), 0, 5)
        self.textPixelValue = QtWidgets.QLineEdit()
        self.textPixelValue.setReadOnly(True)
        self.textPixelValue.setAlignment(QtCore.Qt.AlignHCenter)
        layout.addWidget(self.textPixelValue, 0, 6)

        # RA/Dev
        layout.addWidget(QtWidgets.QLabel('World'), 1, 0)
        layout.addWidget(QtWidgets.QLabel('RA:'), 1, 1)
        self.textWorldX = QtWidgets.QLineEdit()
        self.textWorldX.setReadOnly(True)
        self.textWorldX.setAlignment(QtCore.Qt.AlignHCenter)
        layout.addWidget(self.textWorldX, 1, 2)
        layout.addWidget(QtWidgets.QLabel('DEC:'), 1, 3)
        self.textWorldY = QtWidgets.QLineEdit()
        self.textWorldY.setReadOnly(True)
        self.textWorldY.setAlignment(QtCore.Qt.AlignHCenter)
        layout.addWidget(self.textWorldY, 1, 4)

        # stretch
        layout.setColumnStretch(0, 0)
        layout.setColumnStretch(1, 0)
        layout.setColumnStretch(2, 1)
        layout.setColumnStretch(3, 0)
        layout.setColumnStretch(4, 1)
        layout.setColumnStretch(5, 0)
        layout.setColumnStretch(6, 1)
        layout.setColumnStretch(7, 1)

        # zoom image
        self.labelZoom = QtWidgets.QLabel()
        self.labelZoom.setFixedSize(101, 101)
        self.labelZoom.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.labelZoom.setFrameShadow(QtWidgets.QFrame.Raised)

        # horizontal layout containing info and zoom image
        self.layoutTop = QtWidgets.QHBoxLayout()
        self.layoutTop.addWidget(self.groupInfo)
        self.layoutTop.addWidget(self.labelZoom)
        self.layoutTop.setStretch(0, 1)
        self.layoutTop.setStretch(1, 0)

        # main image
        self.imageView = QImageView()
        self.imageView.mouseMoved.connect(self._mouse_moved)

        # status bar
        self.groupStatus = QtWidgets.QFrame()
        layout = QtWidgets.QHBoxLayout()
        self.groupStatus.setLayout(layout)

        # cuts
        layout.addWidget(QtWidgets.QLabel('Cuts:'))
        self.comboCuts = QtWidgets.QComboBox()
        self.comboCuts.addItems(['100.0%', '99.9%', '99.0%', '95.0%', 'Custom'])
        self.comboCuts.setCurrentText('99.0%')
        self.comboCuts.currentTextChanged.connect(self._cuts_preset_changed)
        layout.addWidget(self.comboCuts)

        # colormap
        spacer = QtWidgets.QSpacerItem(20, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        layout.addSpacerItem(spacer)
        layout.addWidget(QtWidgets.QLabel('Colormap:'))
        self.comboColormap = QtWidgets.QComboBox()
        self.comboColormap.addItems(sorted([cm for cm in plt.colormaps() if not cm.endswith('_r')]))
        self.comboColormap.setCurrentText('gray')
        self.comboColormap.currentTextChanged.connect(self._colormap_changed)
        layout.addWidget(self.comboColormap)
        self.checkColormapReverse = QtWidgets.QCheckBox('reversed')
        self.checkColormapReverse.stateChanged.connect(self._colormap_changed)
        layout.addWidget(self.checkColormapReverse)

        # main layout
        self.layoutMain = QtWidgets.QVBoxLayout()
        self.layoutMain.addLayout(self.layoutTop)
        self.layoutMain.addWidget(self.imageView)
        self.layoutMain.addWidget(self.groupStatus)
        self.layoutMain.setStretch(0, 0)
        self.layoutMain.setStretch(1, 1)
        self.layoutMain.setStretch(2, 0)
        self.setLayout(self.layoutMain)

        # store hdu and (scaled) data
        self.hdu = None
        self.sorted_data = None
        self.scaled_data = None
        self.pixmap = None
        self.cuts = None
        self.wcs = None

    def _apply_cuts(self):
        # get cuts
        c1, c2 = self.cuts

        # scale data
        data = (self.hdu.data - c1) / (c2 - c1)

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

        # now we need to display it
        self.imageView.setImage(image)

    def display(self, hdu):
        # store HDU and create WCS
        self.hdu = hdu
        self.wcs = WCS(hdu.header)

        # store flattened and sorted pixels
        self.sorted_data = np.sort(self.hdu.data.flatten())

        # apply cuts
        self._cuts_preset_changed('99.0%')

    def _cuts_preset_changed(self, preset):
        if preset == 'Custom':
            return

        # get percentage
        percent = float(preset[:-1])

        # get number of pixels to discard at both ends
        n = int(len(self.sorted_data) * (1. - (percent / 100.)))

        # get min/max in cut range
        cut = self.sorted_data[n:-n] if n > 0 else self.sorted_data
        self.cuts = (np.min(cut), np.max(cut))

        # apply them
        self._apply_cuts()

    def _mouse_moved(self, x: float, y: float):
        # show X/Y
        self.textImageX.setText('%.3f' % x)
        self.textImageY.setText('%.3f' % y)

        # convert to RA/Dec and show it
        coord = self.wcs.pixel_to_world([x], [y])
        self.textWorldX.setText(coord.ra.to_string(u.hour, sep=':')[0])
        self.textWorldY.setText(coord.dec.to_string(sep=':')[0])

        # get value
        try:
            value = self.hdu.data[int(y), int(x)]
        except IndexError:
            value = ''
        self.textPixelValue.setText(str(value))

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

    def _colormap_changed(self):
        # get name of colormap
        cm = self.comboColormap.currentText()
        if self.checkColormapReverse.isChecked():
            cm += '_r'

        # set it
        self.imageView.setColormap(cm)


__all__ = ['QFitsView']

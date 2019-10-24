from PyQt5 import QtWidgets, QtCore, QtGui
import numpy as np
from astropy.wcs import WCS
import astropy.units as u
import matplotlib.pyplot as plt
from astropy.wcs.utils import pixel_to_skycoord
from matplotlib import colors
from matplotlib.cm import ScalarMappable

from .norm import *


class QImageView(QtWidgets.QWidget):
    mouseMoved = QtCore.pyqtSignal(float, float)

    def __init__(self, *args, **kwargs):
        QtWidgets.QWidget.__init__(self, *args, **kwargs)
        self._image = None
        self._scaled_pixmap = None
        self._image_rect = None
        self._colormap = None
        self._position_angle = None
        self._mirrored = None

        # set mouse cursor and grab it
        self.setMouseTracking(True)
        self.setCursor(QtCore.Qt.CrossCursor)

        # grab keyboard as well
        self.setFocusPolicy(QtCore.Qt.StrongFocus)

    def setImage(self, image: QtGui.QImage, position_angle: float, mirrored: bool) -> None:
        # set the image
        self._image = image
        self._position_angle = None if position_angle is None else np.radians(position_angle)
        self._mirrored = mirrored

        # update image
        self._update_image()

    def setColormap(self, cm) -> None:
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

        # resize pixmap to my own size keeping aspect ratio and mirror along X axis
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

        # draw coordinate system
        if self._position_angle is not None and self._mirrored is not None:
            self._draw_north_east(painter)

        # remember rect
        self._image_rect = (x, y, pw, ph)

    def _draw_north_east(self, painter):
        # define pen
        pen = QtGui.QPen()
        pen.setColor(QtCore.Qt.red)
        painter.setPen(pen)

        # font
        font = QtGui.QFont('times', 10)
        fm = QtGui.QFontMetrics(font)
        tw = fm.width('N')
        painter.setFont(font)

        # length of line and distance of text
        length = 30
        text = 40

        # draw N line
        x, y = -length * np.sin(self._position_angle), -length * np.cos(self._position_angle)
        painter.drawLine(50, 50, 50 + x, 50 + y)

        # draw N text
        x, y = -text * np.sin(self._position_angle), -text * np.cos(self._position_angle)
        painter.drawText(50 + x - tw/2, 50 + y + tw/2, 'N')

        # angle for E
        east_angle = self._position_angle - (np.pi / 2 if self._mirrored else -np.pi / 2)

        # draw E line
        x, y = -length * np.sin(east_angle), -length * np.cos(east_angle)
        painter.drawLine(50, 50, 50 + x, 50 + y)

        # draw E text
        x, y = -text * np.sin(east_angle), -text * np.cos(east_angle)
        painter.drawText(50 + x - tw/2, 50 + y + tw/2, 'E')

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

    def keyPressEvent(self, event: QtGui.QKeyEvent) -> None:
        # get current cursor position
        cur = QtGui.QCursor()
        pos = cur.pos()

        # decice on key
        if event.key() == QtCore.Qt.Key_Left:
            cur.setPos(pos.x() - 1, pos.y())
        elif event.key() == QtCore.Qt.Key_Right:
            cur.setPos(pos.x() + 1, pos.y())
        elif event.key() == QtCore.Qt.Key_Up:
            cur.setPos(pos.x(), pos.y() - 1)
        elif event.key() == QtCore.Qt.Key_Down:
            cur.setPos(pos.x(), pos.y() + 1)

        # always let parent handle event as well
        QtWidgets.QWidget.keyPressEvent(self, event)


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

        # main image and colorbar
        imageLayout = QtWidgets.QHBoxLayout()
        self.imageView = QImageView()
        self.imageView.mouseMoved.connect(self._mouse_moved)
        imageLayout.addWidget(self.imageView)
        self.labelColorbar = QtWidgets.QLabel()
        self.labelColorbar.setFixedWidth(30)
        self.labelColorbar.setScaledContents(True)
        imageLayout.addWidget(self.labelColorbar)

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
        self.spinLoCut = QtWidgets.QDoubleSpinBox()
        self.spinLoCut.setAlignment(QtCore.Qt.AlignHCenter)
        self.spinLoCut.setRange(-9999999, 9999999)
        self.spinLoCut.valueChanged.connect(self._cuts_changed)
        layout.addWidget(self.spinLoCut)
        self.spinHiCut = QtWidgets.QDoubleSpinBox()
        self.spinHiCut.setAlignment(QtCore.Qt.AlignHCenter)
        self.spinHiCut.setRange(-9999999, 9999999)
        self.spinHiCut.valueChanged.connect(self._cuts_changed)
        layout.addWidget(self.spinHiCut)

        # stretch
        spacer = QtWidgets.QSpacerItem(20, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        layout.addSpacerItem(spacer)
        layout.addWidget(QtWidgets.QLabel('Stretch:'))
        self.comboStretch = QtWidgets.QComboBox()
        self.comboStretch.addItems(['linear', 'log', 'sqrt', 'squared', 'asinh'])
        self.comboStretch.setCurrentText('linear')
        layout.addWidget(self.comboStretch)
        self.comboStretch.currentTextChanged.connect(self._colormap_changed)

        # colormap
        spacer = QtWidgets.QSpacerItem(20, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        layout.addSpacerItem(spacer)
        layout.addWidget(QtWidgets.QLabel('Colormap:'))
        self.comboColormap = QtWidgets.QComboBox()
        self.comboColormap.addItems(sorted([cm for cm in plt.colormaps() if not cm.endswith('_r')]))
        self.comboColormap.setCurrentText('gray')
        layout.addWidget(self.comboColormap)
        self.checkColormapReverse = QtWidgets.QCheckBox('reversed')
        layout.addWidget(self.checkColormapReverse)
        self._colormap_changed()
        self.comboColormap.currentTextChanged.connect(self._colormap_changed)
        self.checkColormapReverse.stateChanged.connect(self._colormap_changed)

        # main layout
        self.layoutMain = QtWidgets.QVBoxLayout()
        self.layoutMain.addLayout(self.layoutTop)
        self.layoutMain.addLayout(imageLayout)
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
        self.position_angle = None
        self.mirrored = None

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

        # flip it
        flipped = image.transformed(QtGui.QTransform().scale(1, -1))

        # now we need to display it
        self.imageView.setImage(flipped, self.position_angle, self.mirrored)

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
        else:
            self.position_angle = None
            self.mirrored = None

        # store flattened and sorted pixels
        self.sorted_data = np.sort(self.hdu.data.flatten())

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
        self.textImageY.setText('%.3f' % y)

        # convert to RA/Dec and show it
        try:
            coord = pixel_to_skycoord(x, y, self.wcs)
            self.textWorldX.setText(coord.ra.to_string(u.hour, sep=':'))
            self.textWorldY.setText(coord.dec.to_string(sep=':'))
        except ValueError:
            self.textWorldX.clear()
            self.textWorldY.clear()

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

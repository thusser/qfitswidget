from typing import Optional

from PyQt5 import QtWidgets, QtCore, QtGui
import numpy as np
from . import resources


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
        self._last_cursor_pos = (0, 0)

        # set mouse cursor and grab it
        self.setMouseTracking(True)
        self.setCursor(QtCore.Qt.CrossCursor)

        # grab keyboard as well
        self.setFocusPolicy(QtCore.Qt.StrongFocus)

    def setImage(self, image: QtGui.QImage, position_angle: Optional[float], mirrored: bool) -> None:
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
        if self._colormap is not None:
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
        painter.drawPixmap(int(x), int(y), self._scaled_pixmap)

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
        painter.drawLine(50, 50, int(50 + x), int(50 + y))

        # draw N text
        x, y = -text * np.sin(self._position_angle), -text * np.cos(self._position_angle)
        painter.drawText(int(50 + x - tw/2), int(50 + y + tw/2), 'N')

        # angle for E
        east_angle = self._position_angle - (np.pi / 2 if self._mirrored else -np.pi / 2)

        # draw E line
        x, y = -length * np.sin(east_angle), -length * np.cos(east_angle)
        painter.drawLine(50, 50, int(50 + x), int(50 + y))

        # draw E text
        x, y = -text * np.sin(east_angle), -text * np.cos(east_angle)
        painter.drawText(int(50 + x - tw/2), int(50 + y + tw/2), 'E')

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
        self._last_cursor_pos = (xi, yi)
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

    @property
    def last_cursor_pos(self) -> (float, float):
        """Returns X/Y position of last cursor position."""
        return self._last_cursor_pos

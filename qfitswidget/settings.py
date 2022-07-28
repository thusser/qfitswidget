from __future__ import annotations
from typing import Optional, TYPE_CHECKING

from PyQt5 import QtWidgets, QtCore, QtGui

if TYPE_CHECKING:
    from .qfitswidget import QFitsWidget
from .qt.settings import Ui_DialogSettings


class Settings(QtWidgets.QDialog, Ui_DialogSettings):
    """PyQt form for displayings settings."""

    def __init__(self, fits_widget: QFitsWidget, parent: Optional[QtWidgets.QWidget] = None):
        """Init new widget."""
        from .qfitswidget import CenterMarkStyle

        QtWidgets.QWidget.__init__(self, parent)
        self.setupUi(self)

        # store
        self.fits_widget = fits_widget

        # center mark styles
        self.comboCenterStyle.addItems([s.value for s in CenterMarkStyle])

        # get values
        self.checkTextOverlayVisible.setChecked(fits_widget.text_overlay_visible)
        self.labelTextOverlayColor.setStyleSheet(f"background-color: {fits_widget.text_overlay_color}")
        self.checkCenterVisible.setChecked(fits_widget.center_mark_visible)
        self.labelCenterColor.setStyleSheet(f"background-color: {fits_widget.center_mark_color}")
        self.comboCenterStyle.setCurrentText(fits_widget.center_mark_style.value)
        self.spinCenterSize.setValue(fits_widget.center_mark_size)
        self.checkDirectionsVisible.setChecked(fits_widget.directions_visible)
        self.labelDirectionsColor.setStyleSheet(f"background-color: {fits_widget.directions_color}")
        self.checkZoomVisible.setChecked(fits_widget.zoom_visible)

        # connect signals
        self.checkTextOverlayVisible.stateChanged.connect(self._text_overlay_visible_changed)
        self.buttonTextOverlayColor.clicked.connect(self._text_overlay_set_color)
        self.checkCenterVisible.stateChanged.connect(self._center_visible_changed)
        self.buttonCenterColor.clicked.connect(self._center_set_color)
        self.comboCenterStyle.currentTextChanged.connect(self._center_set_style)
        self.spinCenterSize.valueChanged.connect(self._center_size_changed)
        self.checkDirectionsVisible.stateChanged.connect(self._directions_visible_changed)
        self.buttonDirectionsColor.clicked.connect(self._directions_set_color)
        self.checkZoomVisible.stateChanged.connect(self._zoom_visible_changed)

    def _text_overlay_visible_changed(self, state: int) -> None:
        self.fits_widget.text_overlay_visible = bool(state)

    def _text_overlay_set_color(self) -> None:
        color = QtWidgets.QColorDialog.getColor(QtGui.QColor(self.fits_widget.text_overlay_color), self)
        self.labelTextOverlayColor.setStyleSheet(f"background-color: {color.name()}")
        self.fits_widget.text_overlay_color = color.name()

    def _center_visible_changed(self, state: int) -> None:
        self.fits_widget.center_mark_visible = bool(state)

    def _center_set_color(self) -> None:
        color = QtWidgets.QColorDialog.getColor(QtGui.QColor(self.fits_widget.center_mark_color), self)
        self.labelCenterColor.setStyleSheet(f"background-color: {color.name()}")
        self.fits_widget.center_mark_color = color.name()

    def _center_set_style(self, style: str) -> None:
        from .qfitswidget import CenterMarkStyle

        self.fits_widget.center_mark_style = CenterMarkStyle(style)

    def _center_size_changed(self, size: int) -> None:
        self.fits_widget.center_mark_size = size

    def _directions_visible_changed(self, state: int) -> None:
        self.fits_widget.directions_visible = bool(state)

    def _directions_set_color(self) -> None:
        color = QtWidgets.QColorDialog.getColor(QtGui.QColor(self.fits_widget.directions_color), self)
        self.labelDirectionsColor.setStyleSheet(f"background-color: {color.name()}")
        self.fits_widget.directions_color = color.name()

    def _zoom_visible_changed(self, state: int) -> None:
        self.fits_widget.zoom_visible = bool(state)


__all__ = ["Settings"]

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
        QtWidgets.QWidget.__init__(self, parent)
        self.setupUi(self)

        # store
        self.fits_widget = fits_widget

        # get values
        self.checkCenterVisible.setChecked(fits_widget.center_mark_visible)
        self.labelCenterColor.setStyleSheet(f"background-color: {fits_widget.center_mark_color}")
        self.checkDirectionsVisible.setChecked(fits_widget.directions_visible)
        self.labelDirectionsColor.setStyleSheet(f"background-color: {fits_widget.directions_color}")

        # connect signals
        self.checkCenterVisible.stateChanged.connect(self._center_visible_changed)
        self.buttonCenterColor.clicked.connect(self._center_set_color)
        self.checkDirectionsVisible.stateChanged.connect(self._directions_visible_changed)
        self.buttonDirectionsColor.clicked.connect(self._directions_set_color)

    def _center_visible_changed(self, state: int) -> None:
        self.fits_widget.center_mark_visible = bool(state)

    def _center_set_color(self) -> None:
        color = QtWidgets.QColorDialog.getColor(QtGui.QColor(self.fits_widget.center_mark_color), self)
        self.labelCenterColor.setStyleSheet(f"background-color: {color.name()}")
        self.fits_widget.center_mark_color = color.name()

    def _directions_visible_changed(self, state: int) -> None:
        self.fits_widget.directions_visible = bool(state)

    def _directions_set_color(self) -> None:
        color = QtWidgets.QColorDialog.getColor(QtGui.QColor(self.fits_widget.directions_color), self)
        self.labelCenterColor.setStyleSheet(f"background-color: {color.name()}")
        self.fits_widget.directions_color = color.name()


__all__ = ["Settings"]

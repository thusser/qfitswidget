from __future__ import annotations
from typing import Any, TYPE_CHECKING

from PyQt5 import QtGui, QtCore
from matplotlib.backend_bases import NavigationToolbar2
from matplotlib.backends.backend_qt import NavigationToolbar2QT

from .settings import Settings
from .qt.resources import *

if TYPE_CHECKING:
    from .qfitswidget import QFitsWidget


class NavigationToolbar(NavigationToolbar2QT):
    toolitems = [*NavigationToolbar2.toolitems]

    # replace subplots with customize
    toolitems[[name for name, *_ in toolitems].index("Subplots")] = (
        "Customize",
        "Customize plot",
        "subplots",
        "customize",
    )

    # append clear overlay button
    toolitems.insert(
        # Add 'customize' action after 'subplots'
        [name for name, *_ in toolitems].index("Customize") + 1,
        ("Clear overlay", "Clear overlay and show image", "image-solid", "clear_overlay"),
    )

    def __init__(self, fits_widget: QFitsWidget, *args: Any, **kwargs: Any):
        NavigationToolbar2QT.__init__(self, *args, **kwargs)
        self.fits_widget = fits_widget
        self.settings = Settings(fits_widget)
        self.show_overlay = True
        self._actions["clear_overlay"].setCheckable(True)
        self._actions["clear_overlay"].setChecked(not fits_widget.show_overlay)

    def _icon(self, name: str) -> QtGui.QIcon:
        # check, whether there is a Qt resource with this name
        filename = f":/resources/{name.replace('png', 'svg')}"
        if QtCore.QFile(filename).exists():
            # yeah, so use it
            pixmap = QtGui.QPixmap(filename)
            mask = pixmap.createMaskFromColor(QtGui.QColor("black"), QtCore.Qt.MaskOutColor)
            pixmap.fill((QtGui.QColor("white")))
            pixmap.setMask(mask)
            return QtGui.QIcon(pixmap)

        else:
            # use MPL icon
            return super()._icon(name)

    def customize(self, *args: Any) -> None:
        if not self.settings.isVisible():
            self.settings.show()

    def clear_overlay(self, *args: Any) -> None:
        self.fits_widget.show_overlay = not self.fits_widget.show_overlay
        self._actions["clear_overlay"].setChecked(not self.fits_widget.show_overlay)


__all__ = ["NavigationToolbar"]

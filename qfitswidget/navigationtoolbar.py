from __future__ import annotations
from typing import Any, TYPE_CHECKING
from matplotlib.backend_bases import NavigationToolbar2
from matplotlib.backends.backend_qt import NavigationToolbar2QT

from .settings import Settings

if TYPE_CHECKING:
    from .qfitswidget import QFitsWidget


class NavigationToolbar(NavigationToolbar2QT):
    toolitems = [*NavigationToolbar2.toolitems]
    toolitems[[name for name, *_ in toolitems].index("Subplots")] = (
        "Customize",
        "Customize plot",
        "subplots",
        "customize",
    )

    def __init__(self, fits_widget: QFitsWidget, *args: Any, **kwargs: Any):
        NavigationToolbar2QT.__init__(self, *args, **kwargs)
        self.settings = Settings(fits_widget)

    def customize(self, *args: Any) -> None:
        if not self.settings.isVisible():
            self.settings.show()


__all__ = ["NavigationToolbar"]

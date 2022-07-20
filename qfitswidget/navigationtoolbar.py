from typing import Any

from matplotlib.backend_bases import NavigationToolbar2
from matplotlib.backends.backend_qt import NavigationToolbar2QT


class NavigationToolbar(NavigationToolbar2QT):
    toolitems = [*NavigationToolbar2.toolitems]
    toolitems[[name for name, *_ in toolitems].index("Subplots")] = (
        "Customize",
        "Customize plot",
        "subplots",
        "customize",
    )

    def customize(self, *args: Any) -> None:
        print("customize")


__all__ = ["NavigationToolbar"]

import sys
from typing import Tuple

from PyQt5 import QtWidgets
from astropy.coordinates import SkyCoord
from astropy.io import fits

from qfitswidget import QFitsWidget, MenuHeader, MenuAction, MenuSeparator


class MainWindow(QtWidgets.QMainWindow):
    def __init__(self, parent=None):
        QtWidgets.QMainWindow.__init__(self, parent)
        self.resize(800, 600)

        self.viewer = QFitsWidget(self)
        self.setCentralWidget(self.viewer)

        self.viewer.set_menu(
            [
                MenuHeader("RA: {{wcs.ra|hms}}, Dec: {{wcs.dec|dms}}"),
                MenuAction("Offset telescope to position", self.offset_telescope),
            ]
        )

        hdu = fits.open(sys.argv[1])
        self.viewer.display(hdu[0])

    def offset_telescope(self, pixel: Tuple[float, float], wcs: SkyCoord):
        print(wcs.dec)


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    wnd = MainWindow()
    wnd.show()
    sys.exit(app.exec_())

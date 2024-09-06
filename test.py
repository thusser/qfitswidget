import sys
from PyQt5 import QtWidgets
from astropy.io import fits

from qfitswidget import QFitsWidget, MenuHeader, MenuAction, MenuSeparator


class MainWindow(QtWidgets.QMainWindow):
    def __init__(self, parent=None):
        QtWidgets.QMainWindow.__init__(self, parent)
        self.resize(800, 600)

        self.viewer = QFitsWidget(self)
        self.setCentralWidget(self.viewer)

        self.viewer.set_menu([
            MenuHeader("Header"),
            MenuAction("click me", lambda: print("clicked")),
            MenuSeparator(),
            MenuAction("End", lambda: print("end"))
        ])

        hdu = fits.open(sys.argv[1])
        self.viewer.display(hdu[0])


if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    wnd = MainWindow()
    wnd.show()
    sys.exit(app.exec_())

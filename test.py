import sys
from PyQt5 import QtWidgets
from astropy.io import fits

from qfitswidget import QFitsWidget


class MainWindow(QtWidgets.QMainWindow):
    def __init__(self, parent=None):
        QtWidgets.QMainWindow.__init__(self, parent)
        self.resize(800, 600)

        self.viewer = QFitsWidget(self)
        self.setCentralWidget(self.viewer)

        hdu = fits.open(sys.argv[1])
        self.viewer.display(hdu[0])


if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    wnd = MainWindow()
    wnd.show()
    sys.exit(app.exec_())

# QFitsWidget

A Qt widget for displaying FITS images, written in Python. It works with PySide6 or PyQt via [qtpy](https://github.com/spyder-ide/qtpy).

## Features

- `QFitsWidget` shows an astropy `PrimaryHDU`, with cuts, stretch and colormap controls.
- When the header has a WCS, the sky position under the mouse is available, for example in the context menu.
- Optional overlays: center mark, compass directions, text overlay and a zoom view. Each one can be switched on and off and has its own color.
- A customizable context menu. Header entries are Jinja templates, so you can show e.g. the RA/Dec of the clicked position.
- `QImageWidget` shows raw image data (not FITS) with the same stretch controls, and `StretchControls` can be used on its own.

## Installation

```bash
pip install qfitswidget
```

You also need a Qt binding, for example `pip install pyside6`.

## Usage

```python
import sys

from astropy.io import fits
from qtpy import QtWidgets

from qfitswidget import QFitsWidget, MenuHeader, MenuAction


def offset_telescope(pixel, wcs):
    print(f"Clicked pixel {pixel}, sky position {wcs}")


app = QtWidgets.QApplication(sys.argv)

viewer = QFitsWidget()
viewer.set_menu(
    [
        MenuHeader("RA: {{wcs.ra|hms}}, Dec: {{wcs.dec|dms}}"),
        MenuAction("Offset telescope to position", offset_telescope),
    ]
)
viewer.display(fits.open(sys.argv[1])[0])
viewer.resize(800, 600)
viewer.show()

sys.exit(app.exec())
```

`test.py` in this repository is a slightly longer version of this example.

## Development

```bash
uv sync
uv run pytest
```

See [CONTRIBUTING.md](CONTRIBUTING.md) for the full workflow.

## License

MIT, see [LICENSE](LICENSE).

### 3rd party

- Using icons from Font Awesome, licensed under CC BY 4.0 (https://creativecommons.org/licenses/by/4.0/).

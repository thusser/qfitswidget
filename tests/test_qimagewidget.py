import numpy as np
import pytest
from pytestqt.qtbot import QtBot
from qtpy import QtGui

from qfitswidget import QImageWidget, StretchParams
from qfitswidget.qimagewidget import render_image


def _pixel(image: QtGui.QImage, x: int, y: int) -> int:
    return QtGui.QColor(image.pixel(x, y)).red()


def test_render_16bit_gray_orientation() -> None:
    data = np.zeros((4, 6), dtype=np.uint16)
    data[0, :] = 65535  # first row is the bottom of the image with origin "lower"
    image = render_image(data, StretchParams(cuts="full"))
    assert (image.width(), image.height()) == (6, 4)
    assert _pixel(image, 0, 3) == 255 and _pixel(image, 0, 0) == 0
    upper = render_image(data, StretchParams(cuts="full"), origin="upper")
    assert _pixel(upper, 0, 0) == 255 and _pixel(upper, 0, 3) == 0


def test_render_source_dtype_decides_full_range() -> None:
    binned = np.full((4, 4), 32768.0, dtype=np.float32)
    image = render_image(binned, StretchParams(cuts="full"), source_dtype="uint16")
    assert _pixel(image, 1, 1) == 128


def test_render_rgb_and_lut() -> None:
    rgb = np.zeros((4, 4, 3), dtype=np.uint8)
    rgb[..., 0] = 255
    image = render_image(rgb)
    colour = QtGui.QColor(image.pixel(0, 0))
    assert (colour.red(), colour.green(), colour.blue()) == (255, 0, 0)

    lut = np.zeros((256, 3), dtype=np.uint8)
    lut[:, 2] = np.arange(256)
    gray = np.full((4, 4), 255, dtype=np.uint8)
    colour = QtGui.QColor(render_image(gray, lut=lut).pixel(0, 0))
    assert (colour.red(), colour.green(), colour.blue()) == (0, 0, 255)

    with pytest.raises(ValueError):
        render_image(np.zeros((4, 4, 2), dtype=np.uint8))


def test_display_renders_in_worker(qtbot: QtBot) -> None:
    widget = QImageWidget()
    qtbot.addWidget(widget)
    widget.display(np.arange(100 * 80, dtype=np.uint16).reshape(100, 80))
    qtbot.waitUntil(lambda: widget.image is not None, timeout=2000)
    assert widget.image is not None and (widget.image.width(), widget.image.height()) == (80, 100)


def test_controls_rerender_last_frame_and_emit_params(qtbot: QtBot) -> None:
    widget = QImageWidget()
    qtbot.addWidget(widget)
    data = np.tile(np.arange(100, dtype=np.uint16), (100, 1))
    widget.display(data)
    qtbot.waitUntil(lambda: widget.image is not None, timeout=2000)
    before = _pixel(widget.image, 50, 50)

    with qtbot.waitSignal(widget.params_changed, timeout=1000) as blocker:
        widget.controls.stretch = "log"
    assert blocker.args[0].stretch == "log"
    qtbot.waitUntil(lambda: _pixel(widget.image, 50, 50) != before, timeout=2000)


def test_manual_cuts_and_percentile_reset(qtbot: QtBot) -> None:
    widget = QImageWidget()
    qtbot.addWidget(widget)
    widget.controls.cuts_mode = "manual"
    widget.controls.set_cut_values(1000, 2000)
    assert widget.stretch_params == StretchParams(cuts="manual", lo=1000, hi=2000)
    # percentiles left over from manual cuts are reset instead of rejected
    widget.controls.cuts_mode = "percentile"
    assert (widget.controls.cut_lo, widget.controls.cut_hi) == (0.5, 99.5)
    assert widget.stretch_params == StretchParams(cuts="percentile", lo=0.5, hi=99.5)
    widget.controls.cuts_mode = "auto"
    assert widget.stretch_params == StretchParams()


def test_invalid_manual_cuts_dont_raise(qtbot: QtBot) -> None:
    widget = QImageWidget()
    qtbot.addWidget(widget)
    widget.display(np.zeros((8, 8), dtype=np.uint16))
    qtbot.waitUntil(lambda: widget.image is not None, timeout=2000)
    # manual needs both cuts, 0 is valid, a percentile range with lo >= hi is not and must just be ignored
    widget.controls.cuts_mode = "percentile"
    widget.controls.spinLoCut.setValue(50)
    widget.controls.spinHiCut.setValue(40)


def test_controls_only_mode(qtbot: QtBot) -> None:
    widget = QImageWidget()
    qtbot.addWidget(widget)
    widget.stretch_locally = False
    with qtbot.waitSignal(widget.params_changed, timeout=1000):
        widget.controls.stretch = "asinh"
    assert widget.image is None

    ready = QtGui.QImage(10, 10, QtGui.QImage.Format.Format_RGB888)
    widget.display_image(ready)
    assert widget.image is ready


def test_set_stretch_params_is_silent(qtbot: QtBot) -> None:
    widget = QImageWidget()
    qtbot.addWidget(widget)
    with qtbot.assertNotEmitted(widget.params_changed):
        widget.set_stretch_params(StretchParams(stretch="sqrt", cuts="manual", lo=1, hi=9))
    assert widget.stretch_params == StretchParams(stretch="sqrt", cuts="manual", lo=1, hi=9)


def test_failed_render_is_reported(qtbot: QtBot) -> None:
    widget = QImageWidget()
    qtbot.addWidget(widget)
    with qtbot.waitSignal(widget.render_failed, timeout=2000):
        widget.display(np.zeros((4, 4, 2), dtype=np.uint8))
    # and the next frame still renders
    widget.display(np.zeros((4, 4), dtype=np.uint8))
    qtbot.waitUntil(lambda: widget.image is not None, timeout=2000)


def test_clear_drops_late_render(qtbot: QtBot) -> None:
    widget = QImageWidget()
    qtbot.addWidget(widget)
    widget.display(np.zeros((4, 4), dtype=np.uint8))
    widget.clear()
    qtbot.wait(200)
    assert widget.image is None and widget.frame is None


def test_newest_frame_wins_while_busy(qtbot: QtBot) -> None:
    widget = QImageWidget()
    qtbot.addWidget(widget)
    for value in range(5):
        widget.display(np.full((4, 4), value * 50, dtype=np.uint8))
    qtbot.waitUntil(lambda: not widget._busy and not widget._pending, timeout=2000)
    assert widget.image is not None and _pixel(widget.image, 0, 0) == 200


def test_view_size_and_resized_signal(qtbot: QtBot) -> None:
    widget = QImageWidget()
    qtbot.addWidget(widget)
    widget.resize(400, 300)
    with qtbot.waitSignal(widget.view_resized, timeout=1000):
        widget.show()
    view = widget.view_size
    assert view.width() == 400 and 0 < view.height() < 300  # the controls take their share


def test_single_channel_3d_is_gray() -> None:
    data = np.full((4, 4, 1), 255, dtype=np.uint8)
    image = render_image(data)
    assert image.format() == QtGui.QImage.Format.Format_Grayscale8

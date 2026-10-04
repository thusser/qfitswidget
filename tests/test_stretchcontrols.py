from pytestqt.qtbot import QtBot
from qtpy import QtCore, QtGui, QtWidgets

from qfitswidget.stretchcontrols import StretchControls


def _controls(qtbot: QtBot, colormap: bool = True, extra: bool = True) -> StretchControls:
    check = QtWidgets.QCheckBox("extra")
    controls = StretchControls(
        ["full", "minmax", "percentile", "manual"],
        ["linear", "sqrt"],
        spin_modes=["percentile", "manual"],
        colormap=colormap,
        extra_checks=[check] if extra else [],
    )
    qtbot.addWidget(controls)
    return controls


def _resize(controls: StretchControls, width: int) -> None:
    controls.resizeEvent(QtGui.QResizeEvent(QtCore.QSize(width, 30), QtCore.QSize(0, 0)))


def test_spins_only_in_spin_modes(qtbot: QtBot) -> None:
    controls = _controls(qtbot)
    controls.show()
    assert controls.cuts_mode == "full"
    assert controls.spinLoCut.isHidden() and controls.spinHiCut.isHidden()
    controls.cuts_mode = "manual"
    assert not controls.spinLoCut.isHidden() and controls.spinLoCut.isEnabled()
    controls.cuts_mode = "minmax"
    assert controls.spinLoCut.isHidden() and not controls.spinLoCut.isEnabled()


def test_changed_signal(qtbot: QtBot) -> None:
    controls = _controls(qtbot)
    controls.cuts_mode = "manual"
    with qtbot.waitSignal(controls.changed, timeout=500):
        controls.spinLoCut.setValue(5)
    with qtbot.waitSignal(controls.changed, timeout=500):
        controls.stretch = "sqrt"
    with qtbot.waitSignal(controls.changed, timeout=500):
        controls.checkColormapReverse.setChecked(True)
    assert controls.colormap == "gray_r"


def test_set_cut_values_is_silent_and_keeps_signals_working(qtbot: QtBot) -> None:
    controls = _controls(qtbot)
    controls.cuts_mode = "manual"
    with qtbot.assertNotEmitted(controls.changed):
        controls.set_cut_values(10, 20)
    assert (controls.cut_lo, controls.cut_hi) == (10, 20)
    # signals of the spin boxes must be back on afterwards
    with qtbot.waitSignal(controls.changed, timeout=500):
        controls.spinHiCut.setValue(30)


def test_disabled_cuts_keep_spins_disabled(qtbot: QtBot) -> None:
    controls = _controls(qtbot)
    controls.cuts_mode = "manual"
    controls.set_cuts_enabled(False)
    assert not controls.spinLoCut.isEnabled()
    controls.set_cuts_enabled(True)
    assert controls.spinLoCut.isEnabled()


def test_overflow_tiers(qtbot: QtBot) -> None:
    controls = _controls(qtbot)
    controls.show()
    extra = controls._overflow_widgets[0]
    reverse = controls.checkColormapReverse
    _resize(controls, 2000)
    assert not controls.labelCuts.isHidden() and controls.buttonOverflow.isHidden()
    assert not controls._overflowed

    # narrower: labels first, then the extra check, then reversed, each only once
    _resize(controls, controls._hide_labels_width - 1)
    assert controls.labelCuts.isHidden() and not controls._overflowed
    assert controls.comboCuts.toolTip() == "Cuts"
    _resize(controls, controls._overflow_widths[0] - 1)
    assert controls._overflowed == {extra}
    _resize(controls, controls._overflow_widths[1] - 1)
    assert controls._overflowed == {extra, reverse}
    assert not controls.buttonOverflow.isHidden()

    # and back, with a pumped event loop so a deferred deletion would crash here
    _resize(controls, 2000)
    QtWidgets.QApplication.processEvents()
    assert not controls._overflowed
    assert controls.buttonOverflow.isHidden()
    assert not controls.labelCuts.isHidden()
    assert not extra.isHidden() and not reverse.isHidden()


def test_no_colormap(qtbot: QtBot) -> None:
    controls = _controls(qtbot, colormap=False, extra=False)
    controls.show()
    assert controls.comboColormap.isHidden() and controls.checkColormapReverse.isHidden()
    _resize(controls, 10)
    assert not controls._overflowed
    assert controls.comboColormap.isHidden()


def test_minimum_size_hint_is_fully_compacted(qtbot: QtBot) -> None:
    controls = _controls(qtbot)
    assert controls.minimumSizeHint().width() <= controls._fully_compacted_width
    assert controls._fully_compacted_width < controls._hide_labels_width

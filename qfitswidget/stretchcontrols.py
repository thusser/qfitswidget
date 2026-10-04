from __future__ import annotations
from typing import Collection, Sequence

import matplotlib.pyplot as plt
from qtpy import QtCore, QtWidgets, QtGui


class StretchControls(QtWidgets.QWidget):
    """Row of display controls (cuts, stretch, optionally colormap) shared by QFitsWidget and QImageWidget.

    As the row runs out of width, it first drops the labels (their text moves to a tooltip on the combo they
    described), then pushes the overflow widgets into a menu, last one first: the colormap's "reversed" checkbox
    is always the last to go, extra checkboxes passed in by the owner go before it.

    The low/high spin boxes are only shown for cuts modes in `spin_modes` (e.g. "Custom"), in all other modes the
    owner calculates the cuts and shows them via set_cut_values().
    """

    changed = QtCore.Signal()
    """Emitted when the user changed cuts, stretch or colormap."""

    def __init__(
        self,
        cuts_modes: Sequence[str],
        stretch_functions: Sequence[str],
        spin_modes: Collection[str] = (),
        colormap: bool = True,
        extra_checks: Sequence[QtWidgets.QCheckBox] = (),
        parent: QtWidgets.QWidget | None = None,
    ):
        """Init new controls.

        Args:
            cuts_modes: Entries of the cuts combo box.
            stretch_functions: Entries of the stretch combo box.
            spin_modes: Cuts modes in which the user enters low/high cuts by hand.
            colormap: Whether to show the colormap controls.
            extra_checks: Checkboxes of the owner, shown at the end of the row and the first to go into the
                overflow menu when it gets narrow. The owner connects to their signals itself.
            parent: Parent widget.
        """
        QtWidgets.QWidget.__init__(self, parent)
        self._spin_modes = set(spin_modes)
        self._colormap = colormap

        self.labelCuts = QtWidgets.QLabel("Cuts:", self)
        self.comboCuts = QtWidgets.QComboBox(self)
        self.comboCuts.addItems(list(cuts_modes))
        self.spinLoCut = QtWidgets.QDoubleSpinBox(self)
        self.spinHiCut = QtWidgets.QDoubleSpinBox(self)
        for spin in (self.spinLoCut, self.spinHiCut):
            spin.setMinimum(-99999.0)
            spin.setMaximum(99999.0)
        self.labelStretch = QtWidgets.QLabel("Stretch:", self)
        self.comboStretch = QtWidgets.QComboBox(self)
        self.comboStretch.addItems(list(stretch_functions))
        self.labelColormap = QtWidgets.QLabel("Colormap:", self)
        self.comboColormap = QtWidgets.QComboBox(self)
        self.comboColormap.addItems(sorted(cm for cm in plt.colormaps() if not cm.endswith("_r")))
        self.comboColormap.setCurrentText("gray")
        self.checkColormapReverse = QtWidgets.QCheckBox("reversed", self)
        self._colormap_widgets: tuple[QtWidgets.QWidget, ...] = (
            self.labelColormap,
            self.comboColormap,
            self.checkColormapReverse,
        )

        # layout
        self.layout_ = QtWidgets.QHBoxLayout(self)
        self.layout_.setContentsMargins(0, 0, 0, 0)

        def spacer() -> QtWidgets.QSpacerItem:
            return QtWidgets.QSpacerItem(5, 20, QtWidgets.QSizePolicy.Policy.Expanding)

        self.layout_.addWidget(self.labelCuts)
        self.layout_.addWidget(self.comboCuts)
        self.layout_.addWidget(self.spinLoCut)
        self.layout_.addWidget(self.spinHiCut)
        self.layout_.addItem(spacer())
        self.layout_.addWidget(self.labelStretch)
        self.layout_.addWidget(self.comboStretch)
        self.layout_.addItem(spacer())
        if colormap:
            self.layout_.addWidget(self.labelColormap)
            self.layout_.addWidget(self.comboColormap)
            self.layout_.addWidget(self.checkColormapReverse)
            self.layout_.addItem(spacer())
        else:
            for widget in self._colormap_widgets:
                widget.setVisible(False)
        for check in extra_checks:
            self.layout_.addWidget(check)

        # signals, spin boxes only matter in the modes they are shown for (see _update_spins())
        self.comboCuts.currentTextChanged.connect(self._cuts_changed)
        self.comboStretch.currentTextChanged.connect(self.changed)
        self.comboColormap.currentTextChanged.connect(self.changed)
        self.checkColormapReverse.toggled.connect(self.changed)
        self.spinLoCut.valueChanged.connect(self.changed)
        self.spinHiCut.valueChanged.connect(self.changed)
        self._update_spins()

        # responsive row, thresholds are measured against the row's real sizeHint() at each tier rather than
        # hardcoded: a pixel constant picked once against one font/DPI/style silently drifts when that changes
        self._overflow_widgets: tuple[QtWidgets.QWidget, ...] = (
            (*extra_checks, self.checkColormapReverse) if colormap else tuple(extra_checks)
        )
        (
            self._hide_labels_width,
            self._overflow_widths,
            self._fully_compacted_width,
        ) = self._measure_tier_widths()
        self._overflow_menu = QtWidgets.QMenu(self)
        # One QWidgetAction per overflow-able widget, created once and reused for the widget's whole lifetime,
        # never deleted: creating a fresh one on every overflow and deleteLater()'ing it on restore crashed once
        # a real event loop processed the deferred deletion. Reusing one and only toggling its menu membership
        # sidesteps that.
        self._overflow_actions: dict[QtWidgets.QWidget, QtWidgets.QWidgetAction] = {
            widget: QtWidgets.QWidgetAction(self._overflow_menu) for widget in self._overflow_widgets
        }
        self._overflowed: set[QtWidgets.QWidget] = set()
        self.buttonOverflow = QtWidgets.QToolButton(self)
        self.buttonOverflow.setText("⋯")  # horizontal ellipsis, no icon dependency needed
        self.buttonOverflow.setToolTip("More display options")
        self.buttonOverflow.setPopupMode(QtWidgets.QToolButton.ToolButtonPopupMode.InstantPopup)
        self.buttonOverflow.setMenu(self._overflow_menu)
        self.buttonOverflow.setVisible(False)
        self.layout_.addWidget(self.buttonOverflow)

    # ── values ─────────────────────────────────────────────────────────────

    @property
    def cuts_mode(self) -> str:
        return str(self.comboCuts.currentText())

    @cuts_mode.setter
    def cuts_mode(self, mode: str) -> None:
        self.comboCuts.setCurrentText(mode)

    @property
    def cut_lo(self) -> float:
        return float(self.spinLoCut.value())

    @property
    def cut_hi(self) -> float:
        return float(self.spinHiCut.value())

    @property
    def stretch(self) -> str:
        return str(self.comboStretch.currentText())

    @stretch.setter
    def stretch(self, stretch: str) -> None:
        self.comboStretch.setCurrentText(stretch)

    @property
    def colormap(self) -> str:
        """Name of the colormap, with "_r" appended if reversed."""
        name = str(self.comboColormap.currentText())
        return name + "_r" if self.checkColormapReverse.isChecked() else name

    @colormap.setter
    def colormap(self, name: str) -> None:
        self.comboColormap.setCurrentText(name)

    def set_cut_values(self, lo: float, hi: float) -> None:
        """Set the cut values shown in the spin boxes, without emitting `changed`."""
        for spin, value in ((self.spinLoCut, lo), (self.spinHiCut, hi)):
            blocked = spin.blockSignals(True)
            spin.setValue(value)
            spin.blockSignals(blocked)

    def set_cuts_enabled(self, enabled: bool) -> None:
        for widget in (self.labelCuts, self.comboCuts):
            widget.setEnabled(enabled)
        self._update_spins(enabled)

    def set_stretch_enabled(self, enabled: bool) -> None:
        for widget in (self.labelStretch, self.comboStretch):
            widget.setEnabled(enabled)

    def set_colormap_enabled(self, enabled: bool) -> None:
        for widget in self._colormap_widgets:
            widget.setEnabled(enabled)

    # ── cuts spin boxes ────────────────────────────────────────────────────

    def _cuts_changed(self) -> None:
        self._update_spins()
        self.changed.emit()

    def _update_spins(self, enabled: bool | None = None) -> None:
        """Show the spin boxes only in cuts modes where the user enters values, enabled with the combo box."""
        if enabled is None:
            enabled = self.comboCuts.isEnabled()
        manual = self.cuts_mode in self._spin_modes
        for spin in (self.spinLoCut, self.spinHiCut):
            spin.setVisible(manual)
            spin.setEnabled(manual and enabled)

    # ── responsive row ─────────────────────────────────────────────────────

    def _measure_tier_widths(self) -> tuple[int, list[int], int]:
        """Derives the resizeEvent() thresholds from the layout's own real sizeHint() at each tier: toggles the
        relevant widgets' visibility, reads sizeHint(), restores everything to fully visible afterward. Runs
        once, at construction, the numbers are fixed for the widget's lifetime.

        Returns:
            Width below which the labels are hidden, widths below which each overflow widget goes into the menu
            (same order as the overflow widgets), and the fully compacted width, which minimumSizeHint() reports.
            A little margin is added so a resize near a boundary doesn't flicker. Note that a threshold is
            measured with its own widget still visible, but the floor with all of them already hidden.
        """
        margin = 8
        labels = [self.labelCuts, self.labelStretch] + ([self.labelColormap] if self._colormap else [])

        widths = [self.layout_.sizeHint().width()]
        for label in labels:
            label.setVisible(False)
        widths.append(self.layout_.sizeHint().width())
        for widget in self._overflow_widgets:
            widget.setVisible(False)
            widths.append(self.layout_.sizeHint().width())

        for widget in (*labels, *self._overflow_widgets):
            widget.setVisible(True)

        return widths[0] + margin, [w + margin for w in widths[1:-1]], widths[-1] + margin

    def minimumSizeHint(self) -> QtCore.QSize:
        """Reports the fully compacted width as the floor, not what the row's current state happens to need.

        Matters inside a resizable QScrollArea: Qt decides between shrinking a widget and showing a scrollbar
        based on minimumSizeHint() before ever delivering a smaller resizeEvent. With the default, the scroll area
        concludes "this needs ~600px", shows a scrollbar, and resizeEvent() never gets narrow enough to trigger
        the hide/overflow logic at all."""
        hint = super().minimumSizeHint()
        return QtCore.QSize(min(hint.width(), self._fully_compacted_width), hint.height())

    # Gap between a tier's hide threshold and its re-show threshold. Without it a width sitting right at a
    # boundary, which happens in practice (a live drag delivers resize events a couple of pixels apart, and
    # reparenting a widget out of/into the layout can itself trigger a follow-up resize), flips the tier on every
    # event, which flickers.
    _HYSTERESIS_MARGIN = 24

    def _tier_active(self, width: int, threshold: int, currently_active: bool) -> bool:
        """Whether a hide/overflow tier should be active at this width: to activate, the width has to be below
        `threshold`, to deactivate again it has to clear `threshold + _HYSTERESIS_MARGIN`."""
        if currently_active:
            return width < threshold + self._HYSTERESIS_MARGIN
        return width < threshold

    def resizeEvent(self, event: QtGui.QResizeEvent) -> None:
        super().resizeEvent(event)
        width = event.size().width()

        show_labels = not self._tier_active(width, self._hide_labels_width, self.labelCuts.isHidden())
        self.labelCuts.setVisible(show_labels)
        self.labelStretch.setVisible(show_labels)
        self.comboCuts.setToolTip("" if show_labels else "Cuts")
        self.comboStretch.setToolTip("" if show_labels else "Stretch")
        if self._colormap:
            self.labelColormap.setVisible(show_labels)
            self.comboColormap.setToolTip("" if show_labels else "Colormap")

        # each _set_overflow() call is independent and idempotent, the order of the widgets is the priority
        for widget, threshold in zip(self._overflow_widgets, self._overflow_widths):
            self._set_overflow(widget, self._tier_active(width, threshold, widget in self._overflowed))

    def _set_overflow(self, widget: QtWidgets.QWidget, overflow: bool) -> None:
        """Moves widget between the layout and the overflow menu: the actual instance either way, not a copy, so
        its signal connections and state survive the move. QWidgetAction.setDefaultWidget() is the standard Qt
        way to embed a real interactive widget in a QMenu."""
        if overflow == (widget in self._overflowed):
            return
        action = self._overflow_actions[widget]
        if overflow:
            self.layout_.removeWidget(widget)
            action.setDefaultWidget(widget)
            self._overflow_menu.addAction(action)
            self._overflowed.add(widget)
        else:
            self._overflow_menu.removeAction(action)
            action.releaseWidget(widget)
            # setVisible(True) has to come AFTER addWidget(): reparenting hides a widget as a side effect
            self.layout_.insertWidget(self.layout_.indexOf(self.buttonOverflow), widget)
            widget.setVisible(True)
            self._overflowed.discard(widget)
        self.buttonOverflow.setVisible(len(self._overflowed) > 0)

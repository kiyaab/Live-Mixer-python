"""Single channel strip widget."""

from __future__ import annotations

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QDoubleSpinBox,
    QFrame,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QSlider,
    QVBoxLayout,
    QWidget,
)

from gui.meters import LevelMeter


class ChannelStrip(QFrame):
    """One mixer channel: gain, meter, fader, pan, mute, solo."""

    gain_changed = Signal(int, float)
    fader_changed = Signal(int, float)
    pan_changed = Signal(int, float)
    mute_changed = Signal(int, bool)
    solo_changed = Signal(int, bool)

    FADER_MIN_DB = -60.0
    FADER_MAX_DB = 10.0

    def __init__(self, index: int, name: str = "CH", parent=None) -> None:
        super().__init__(parent)
        self.index = index
        self.setFrameStyle(QFrame.Shape.StyledPanel | QFrame.Shadow.Raised)
        self.setStyleSheet(
            "ChannelStrip { background-color: #222228; border: 1px solid #333; border-radius: 6px; }"
        )
        self.setFixedWidth(100)

        layout = QVBoxLayout(self)
        layout.setSpacing(4)
        layout.setContentsMargins(6, 8, 6, 8)

        self.name_label = QLabel(name)
        self.name_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.name_label.setStyleSheet("font-weight: bold; color: #4a9eff;")
        layout.addWidget(self.name_label)

        layout.addWidget(QLabel("Gain"))
        self.gain_spin = QDoubleSpinBox()
        self.gain_spin.setRange(-20.0, 20.0)
        self.gain_spin.setSingleStep(0.5)
        self.gain_spin.setSuffix(" dB")
        self.gain_spin.valueChanged.connect(self._on_gain_changed)
        layout.addWidget(self.gain_spin)

        self.meter = LevelMeter()
        layout.addWidget(self.meter, alignment=Qt.AlignmentFlag.AlignCenter)

        self.fader = QSlider(Qt.Orientation.Vertical)
        self.fader.setRange(0, 700)
        self.fader.setValue(self._db_to_slider(0.0))
        self.fader.setMinimumHeight(140)
        self.fader.valueChanged.connect(self._on_fader_changed)
        layout.addWidget(self.fader, alignment=Qt.AlignmentFlag.AlignCenter)

        self.fader_label = QLabel("0.0 dB")
        self.fader_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.fader_label.setStyleSheet("font-size: 10px; color: #888;")
        layout.addWidget(self.fader_label)

        pan_row = QHBoxLayout()
        pan_row.addWidget(QLabel("L"))
        self.pan_slider = QSlider(Qt.Orientation.Horizontal)
        self.pan_slider.setRange(-100, 100)
        self.pan_slider.setValue(0)
        self.pan_slider.valueChanged.connect(self._on_pan_changed)
        pan_row.addWidget(self.pan_slider)
        pan_row.addWidget(QLabel("R"))
        layout.addLayout(pan_row)

        btn_row = QHBoxLayout()
        self.mute_btn = QPushButton("M")
        self.mute_btn.setCheckable(True)
        self.mute_btn.setFixedSize(32, 28)
        self.mute_btn.toggled.connect(self._on_mute_toggled)
        btn_row.addWidget(self.mute_btn)

        self.solo_btn = QPushButton("S")
        self.solo_btn.setObjectName("soloButton")
        self.solo_btn.setCheckable(True)
        self.solo_btn.setFixedSize(32, 28)
        self.solo_btn.toggled.connect(self._on_solo_toggled)
        btn_row.addWidget(self.solo_btn)
        layout.addLayout(btn_row)

    @staticmethod
    def _db_to_slider(db: float) -> int:
        clamped = max(ChannelStrip.FADER_MIN_DB, min(ChannelStrip.FADER_MAX_DB, db))
        return int((clamped - ChannelStrip.FADER_MIN_DB) * 10)

    @staticmethod
    def _slider_to_db(value: int) -> float:
        return ChannelStrip.FADER_MIN_DB + value / 10.0

    def _on_gain_changed(self, value: float) -> None:
        self.gain_changed.emit(self.index, value)

    def _on_fader_changed(self, value: int) -> None:
        db = self._slider_to_db(value)
        self.fader_label.setText(f"{db:.1f} dB")
        self.fader_changed.emit(self.index, db)

    def _on_pan_changed(self, value: int) -> None:
        self.pan_changed.emit(self.index, value / 100.0)

    def _on_mute_toggled(self, checked: bool) -> None:
        self.mute_changed.emit(self.index, checked)

    def _on_solo_toggled(self, checked: bool) -> None:
        self.solo_changed.emit(self.index, checked)

    def set_levels(self, peak: float, rms: float, peak_hold: float, clipped: bool) -> None:
        self.meter.set_levels(peak, rms, peak_hold, clipped)

    def set_gain_db(self, db: float) -> None:
        self.gain_spin.blockSignals(True)
        self.gain_spin.setValue(db)
        self.gain_spin.blockSignals(False)

    def set_fader_db(self, db: float) -> None:
        self.fader.blockSignals(True)
        self.fader.setValue(self._db_to_slider(db))
        self.fader_label.setText(f"{db:.1f} dB")
        self.fader.blockSignals(False)

    def set_pan(self, pan: float) -> None:
        self.pan_slider.blockSignals(True)
        self.pan_slider.setValue(int(pan * 100))
        self.pan_slider.blockSignals(False)

    def set_mute(self, muted: bool) -> None:
        self.mute_btn.blockSignals(True)
        self.mute_btn.setChecked(muted)
        self.mute_btn.blockSignals(False)

    def set_solo(self, soloed: bool) -> None:
        self.solo_btn.blockSignals(True)
        self.solo_btn.setChecked(soloed)
        self.solo_btn.blockSignals(False)

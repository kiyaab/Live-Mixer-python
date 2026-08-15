"""Master section widget."""

from __future__ import annotations

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import QFrame, QLabel, QSlider, QVBoxLayout

from gui.channel_strip import ChannelStrip
from gui.meters import LevelMeter


class MasterSection(QFrame):
    """Master fader and output meter."""

    gain_changed = Signal(float)

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.setFrameStyle(QFrame.Shape.StyledPanel | QFrame.Shadow.Raised)
        self.setStyleSheet(
            "MasterSection { background-color: #282830; border: 2px solid #4a9eff; border-radius: 6px; }"
        )
        self.setFixedWidth(100)

        layout = QVBoxLayout(self)
        layout.setSpacing(4)
        layout.setContentsMargins(8, 8, 8, 8)

        title = QLabel("MASTER")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet("font-weight: bold; color: #fff; font-size: 13px;")
        layout.addWidget(title)

        self.meter = LevelMeter()
        layout.addWidget(self.meter, alignment=Qt.AlignmentFlag.AlignCenter)

        self.fader = QSlider(Qt.Orientation.Vertical)
        self.fader.setRange(0, 700)
        self.fader.setValue(ChannelStrip._db_to_slider(0.0))
        self.fader.setMinimumHeight(160)
        self.fader.valueChanged.connect(self._on_fader_changed)
        layout.addWidget(self.fader, alignment=Qt.AlignmentFlag.AlignCenter)

        self.fader_label = QLabel("0.0 dB")
        self.fader_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.fader_label.setStyleSheet("font-size: 10px; color: #aaa;")
        layout.addWidget(self.fader_label)

    def _on_fader_changed(self, value: int) -> None:
        db = ChannelStrip._slider_to_db(value)
        self.fader_label.setText(f"{db:.1f} dB")
        self.gain_changed.emit(db)

    def set_levels(self, peak: float, rms: float, peak_hold: float, clipped: bool) -> None:
        self.meter.set_levels(peak, rms, peak_hold, clipped)

    def set_gain_db(self, db: float) -> None:
        self.fader.blockSignals(True)
        self.fader.setValue(ChannelStrip._db_to_slider(db))
        self.fader_label.setText(f"{db:.1f} dB")
        self.fader.blockSignals(False)

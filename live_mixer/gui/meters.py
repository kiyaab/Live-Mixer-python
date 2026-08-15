"""Level meter widgets."""

from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtGui import QColor, QPainter, QPen
from PySide6.QtWidgets import QWidget

from gui.styles import METER_BG, METER_CLIP, METER_GREEN, METER_RED, METER_YELLOW
from utils.parameters import linear_to_db


class LevelMeter(QWidget):
    """Vertical peak/RMS level meter with clip indicator."""

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self._peak = 0.0
        self._rms = 0.0
        self._peak_hold = 0.0
        self._clipped = False
        self.setMinimumSize(16, 120)
        self.setMaximumWidth(24)

    def set_levels(
        self,
        peak: float,
        rms: float,
        peak_hold: float,
        clipped: bool,
    ) -> None:
        self._peak = max(0.0, min(1.0, peak))
        self._rms = max(0.0, min(1.0, rms))
        self._peak_hold = max(0.0, min(1.0, peak_hold))
        self._clipped = clipped
        self.update()

    def paintEvent(self, event) -> None:
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        w = self.width()
        h = self.height()
        margin = 2
        bar_w = w - margin * 2

        painter.fillRect(0, 0, w, h, QColor(METER_BG))

        def db_to_height(level: float) -> int:
            if level <= 0.0:
                return 0
            db = linear_to_db(level, floor_db=-60.0)
            normalized = (db + 60.0) / 60.0
            return int(normalized * (h - margin * 2))

        rms_h = db_to_height(self._rms)
        peak_h = db_to_height(self._peak)
        hold_h = db_to_height(self._peak_hold)

        rms_y = h - margin - rms_h
        painter.fillRect(margin, rms_y, bar_w, rms_h, QColor(METER_GREEN))

        peak_y = h - margin - peak_h
        painter.setPen(QPen(QColor(METER_YELLOW), 2))
        painter.drawLine(margin, peak_y, margin + bar_w, peak_y)

        hold_y = h - margin - hold_h
        painter.setPen(QPen(QColor("#ffffff"), 1))
        painter.drawLine(margin, hold_y, margin + bar_w, hold_y)

        if self._clipped:
            painter.fillRect(margin, margin, bar_w, 4, QColor(METER_CLIP))

        painter.end()

"""Mixer view — horizontal channel strips and master section."""

from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QHBoxLayout, QScrollArea, QWidget

from gui.channel_strip import ChannelStrip
from gui.master_section import MasterSection


class MixerView(QWidget):
    """Scrollable row of channel strips plus master section."""

    def __init__(self, num_channels: int = 4, parent=None) -> None:
        super().__init__(parent)
        self._strips: list[ChannelStrip] = []

        outer = QHBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        scroll.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

        strip_container = QWidget()
        strip_layout = QHBoxLayout(strip_container)
        strip_layout.setSpacing(8)
        strip_layout.setContentsMargins(8, 8, 8, 8)

        for i in range(num_channels):
            strip = ChannelStrip(i, f"CH{i + 1}")
            self._strips.append(strip)
            strip_layout.addWidget(strip)

        strip_layout.addStretch()
        scroll.setWidget(strip_container)
        outer.addWidget(scroll, stretch=1)

        self.master = MasterSection()
        outer.addWidget(self.master)

    @property
    def channel_strips(self) -> list[ChannelStrip]:
        return self._strips

    def update_meters(self, meter_data: dict) -> None:
        channels = meter_data.get("channels", [])
        for i, strip in enumerate(self._strips):
            if i < len(channels):
                ch = channels[i]
                strip.set_levels(
                    ch["peak"], ch["rms"], ch["peak_hold"], ch["clipped"]
                )

        master = meter_data.get("master", {})
        self.master.set_levels(
            master.get("peak", 0.0),
            master.get("rms", 0.0),
            master.get("peak_hold", 0.0),
            master.get("clipped", False),
        )

    def load_channel_states(self, states: list) -> None:
        for i, strip in enumerate(self._strips):
            if i < len(states):
                s = states[i]
                strip.set_gain_db(s.input_gain_db)
                strip.set_fader_db(s.fader_db)
                strip.set_pan(s.pan)
                strip.set_mute(s.mute)
                strip.set_solo(s.solo)

    def load_master_gain(self, gain_db: float) -> None:
        self.master.set_gain_db(gain_db)

    def connect_engine(self, engine) -> None:
        """Wire strip signals to audio engine control methods."""
        for strip in self._strips:
            strip.gain_changed.connect(
                lambda idx, db, e=engine: e.set_channel_gain(idx, db)
            )
            strip.fader_changed.connect(
                lambda idx, db, e=engine: e.set_channel_fader(idx, db)
            )
            strip.pan_changed.connect(
                lambda idx, pan, e=engine: e.set_channel_pan(idx, pan)
            )
            strip.mute_changed.connect(
                lambda idx, muted, e=engine: e.set_channel_mute(idx, muted)
            )
            strip.solo_changed.connect(
                lambda idx, solo, e=engine: e.set_channel_solo(idx, solo)
            )

        self.master.gain_changed.connect(engine.set_master_gain)

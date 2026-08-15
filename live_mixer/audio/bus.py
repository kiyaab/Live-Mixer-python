"""Mix bus for summing channel outputs."""

from __future__ import annotations

from enum import Enum, auto

import numpy as np

from audio.dsp.metering import MeterState, PeakRMSMeter


class BusType(Enum):
    MAIN = auto()
    MONITOR = auto()
    FX = auto()
    RECORD = auto()


class Bus:
    """Summing bus with stereo accumulation and metering."""

    def __init__(self, name: str, bus_type: BusType = BusType.MAIN, sample_rate: int = 48000):
        self.name = name
        self.bus_type = bus_type
        self._meter = PeakRMSMeter(sample_rate=sample_rate)

    def sum_stereo(
        self,
        left: np.ndarray,
        right: np.ndarray,
        mix_l: np.ndarray,
        mix_r: np.ndarray,
        num_frames: int,
        gain: float = 1.0,
    ) -> None:
        """Add stereo signal into mix buffers (in-place)."""
        mix_l[:num_frames] += left[:num_frames] * gain
        mix_r[:num_frames] += right[:num_frames] * gain

    def update_meter(self, left: np.ndarray, right: np.ndarray, num_frames: int) -> MeterState:
        """Update bus meter from stereo output."""
        stereo = np.empty((num_frames, 2), dtype=np.float32)
        stereo[:, 0] = left[:num_frames]
        stereo[:, 1] = right[:num_frames]
        return self._meter.process(stereo)

    @property
    def meter_state(self) -> MeterState:
        return self._meter.state

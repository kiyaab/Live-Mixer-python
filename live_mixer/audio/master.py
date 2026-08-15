"""Master output section with gain and metering."""

from __future__ import annotations

import numpy as np

from audio.dsp.gain import Gain
from audio.dsp.metering import MeterState, PeakRMSMeter


class MasterSection:
    """Master bus gain and stereo output metering."""

    def __init__(self, gain_db: float = 0.0, sample_rate: int = 48000) -> None:
        self.gain = Gain(gain_db)
        self._meter = PeakRMSMeter(sample_rate=sample_rate)

    def set_gain_db(self, gain_db: float) -> None:
        self.gain.set_gain_db(gain_db)

    @property
    def meter_state(self) -> MeterState:
        return self._meter.state

    def process(
        self,
        left: np.ndarray,
        right: np.ndarray,
        out: np.ndarray,
        num_frames: int,
    ) -> None:
        """
        Apply master gain and write interleaved stereo to output buffer.

        Args:
            left: Left mix buffer.
            right: Right mix buffer.
            out: Output buffer shape (frames, 2).
            num_frames: Number of frames to process.
        """
        out_view = out[:num_frames]
        out_view[:, 0] = self.gain.process(left[:num_frames])
        out_view[:, 1] = self.gain.process(right[:num_frames])
        self._meter.process(out_view)

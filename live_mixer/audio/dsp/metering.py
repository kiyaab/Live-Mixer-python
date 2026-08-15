"""Level metering for peak, RMS, and clip detection."""

from __future__ import annotations

import math
from dataclasses import dataclass, field

import numpy as np


@dataclass
class MeterState:
    """Meter readings transferred from audio thread to GUI."""

    peak: float = 0.0
    rms: float = 0.0
    peak_hold: float = 0.0
    clipped: bool = False
    gain_reduction_db: float = 0.0


class PeakRMSMeter:
    """
    Real-time peak and RMS meter with peak hold and clip detection.

    Designed for use inside the audio callback with minimal allocation.
    """

    CLIP_THRESHOLD = 0.999

    def __init__(self, hold_seconds: float = 1.5, sample_rate: int = 48000) -> None:
        self._hold_samples = int(hold_seconds * sample_rate)
        self._hold_counter = 0
        self._peak_hold = 0.0
        self.state = MeterState()

    def reset(self) -> None:
        self._hold_counter = 0
        self._peak_hold = 0.0
        self.state = MeterState()

    def process(self, audio: np.ndarray) -> MeterState:
        """
        Analyze an audio block and update meter state.

        Args:
            audio: Mono or multichannel float32 samples.

        Returns:
            Updated MeterState (same object, reused each call).
        """
        if audio.size == 0:
            return self.state

        mono = audio if audio.ndim == 1 else np.max(np.abs(audio), axis=1)
        peak = float(np.max(np.abs(mono)))
        rms = float(math.sqrt(np.mean(mono * mono)))

        if peak >= self._peak_hold:
            self._peak_hold = peak
            self._hold_counter = self._hold_samples
        elif self._hold_counter > 0:
            self._hold_counter -= mono.shape[0]
        else:
            self._peak_hold = peak

        self.state.peak = peak
        self.state.rms = rms
        self.state.peak_hold = self._peak_hold
        self.state.clipped = peak >= self.CLIP_THRESHOLD
        return self.state

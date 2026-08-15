"""Single mixer channel with input gain, fader, pan, mute, and solo."""

from __future__ import annotations

from dataclasses import dataclass, field

import numpy as np

from audio.dsp.gain import Gain
from audio.dsp.metering import MeterState, PeakRMSMeter


def pan_to_stereo_gains(pan: float) -> tuple[float, float]:
    """
    Constant-power pan law.

    Args:
        pan: -1.0 (full left) to +1.0 (full right), 0.0 = center.

    Returns:
        (left_gain, right_gain) linear amplitudes.
    """
    pan_clamped = max(-1.0, min(1.0, pan))
    angle = (pan_clamped + 1.0) * 0.25 * np.pi
    return float(np.cos(angle)), float(np.sin(angle))


@dataclass
class ChannelState:
    """Snapshot of channel parameters for presets/GUI."""

    name: str = "CH"
    input_gain_db: float = 0.0
    fader_db: float = 0.0
    pan: float = 0.0
    mute: bool = False
    solo: bool = False
    phase_invert: bool = False


class Channel:
    """
    Independent mixer channel with gain staging and metering.

    Processing chain (Phase 1): Input Gain → Fader → Pan → Mute/Solo
    Additional DSP stages plug in between gain and fader in later phases.
    """

    def __init__(
        self,
        name: str = "CH",
        input_gain_db: float = 0.0,
        fader_db: float = 0.0,
        sample_rate: int = 48000,
    ) -> None:
        self.name = name
        self.input_gain = Gain(input_gain_db)
        self.fader = Gain(fader_db)
        self._pan = 0.0
        self._mute = False
        self._solo = False
        self._phase_invert = False
        self._meter = PeakRMSMeter(sample_rate=sample_rate)
        self._left_out = np.zeros(0, dtype=np.float32)
        self._right_out = np.zeros(0, dtype=np.float32)

    # --- Control interface (called from GUI/control thread) ---

    def set_gain(self, gain_db: float) -> None:
        self.input_gain.set_gain_db(gain_db)

    def set_fader(self, fader_db: float) -> None:
        self.fader.set_gain_db(fader_db)

    def set_pan(self, pan: float) -> None:
        self._pan = max(-1.0, min(1.0, pan))

    def mute(self, muted: bool = True) -> None:
        self._mute = muted

    def solo(self, soloed: bool = True) -> None:
        self._solo = soloed

    def set_phase_invert(self, invert: bool) -> None:
        self._phase_invert = invert

    @property
    def is_muted(self) -> bool:
        return self._mute

    @property
    def is_solo(self) -> bool:
        return self._solo

    @property
    def pan(self) -> float:
        return self._pan

    @property
    def meter_state(self) -> MeterState:
        return self._meter.state

    def get_state(self) -> ChannelState:
        return ChannelState(
            name=self.name,
            input_gain_db=self.input_gain.gain_db,
            fader_db=self.fader.gain_db,
            pan=self._pan,
            mute=self._mute,
            solo=self._solo,
            phase_invert=self._phase_invert,
        )

    def apply_state(self, state: ChannelState) -> None:
        self.name = state.name
        self.set_gain(state.input_gain_db)
        self.set_fader(state.fader_db)
        self.set_pan(state.pan)
        self.mute(state.mute)
        self.solo(state.solo)
        self.set_phase_invert(state.phase_invert)

    # --- Real-time processing (audio callback thread) ---

    def process(
        self,
        audio: np.ndarray,
        num_frames: int,
        solo_active: bool,
        any_solo: bool,
    ) -> tuple[np.ndarray, np.ndarray]:
        """
        Process mono input into stereo output.

        Args:
            audio: Mono input block (at least num_frames samples).
            num_frames: Number of frames to process.
            solo_active: True if any channel is soloed.
            any_solo: Alias for solo_active (for clarity in mixer).

        Returns:
            (left, right) stereo output views into internal buffers.
        """
        if self._left_out.shape[0] < num_frames:
            self._left_out = np.zeros(num_frames, dtype=np.float32)
            self._right_out = np.zeros(num_frames, dtype=np.float32)

        mono = audio[:num_frames]
        processed = self.input_gain.process(mono)

        if self._phase_invert:
            processed = -processed

        # Placeholder for future DSP chain (EQ, gate, compressor, etc.)
        processed = self.fader.process(processed)

        left_gain, right_gain = pan_to_stereo_gains(self._pan)
        left = self._left_out[:num_frames]
        right = self._right_out[:num_frames]
        np.copyto(left, processed * left_gain)
        np.copyto(right, processed * right_gain)

        if self._mute or (any_solo and not self._solo):
            left.fill(0.0)
            right.fill(0.0)

        self._meter.process(processed)
        return left, right

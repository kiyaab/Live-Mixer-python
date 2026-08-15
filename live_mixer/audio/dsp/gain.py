"""Gain processing with smooth parameter changes."""

from __future__ import annotations

import numpy as np

from utils.parameters import SmoothParameter, db_to_linear


class Gain:
    """
    Gain stage with dB control and click-free smoothing.

    Processes audio in-place when an output buffer is provided.
    """

    def __init__(self, gain_db: float = 0.0, smoothing_coeff: float = 0.05) -> None:
        linear = db_to_linear(gain_db)
        self._gain = SmoothParameter(linear, linear, smoothing_coeff)

    @property
    def gain_db(self) -> float:
        from utils.parameters import linear_to_db

        return linear_to_db(self._gain.target)

    def set_gain_db(self, gain_db: float) -> None:
        """Set target gain in decibels (control thread)."""
        self._gain.set_target(db_to_linear(gain_db))

    def set_gain_linear(self, linear: float) -> None:
        """Set target gain as linear amplitude (control thread)."""
        self._gain.set_target(linear)

    def process(self, audio: np.ndarray, out: np.ndarray | None = None) -> np.ndarray:
        """
        Apply smoothed gain to audio block.

        Args:
            audio: Input samples, shape (frames,) or (frames, channels).
            out: Optional preallocated output buffer.

        Returns:
            Processed audio (same shape as input).
        """
        num_samples = audio.shape[0]
        gain_block = self._gain.process_block(num_samples)

        if audio.ndim == 1:
            result = audio * gain_block
        else:
            result = audio * gain_block[:, np.newaxis]

        if out is not None:
            np.copyto(out, result)
            return out
        return result.astype(np.float32, copy=False)

    def reset(self, gain_db: float = 0.0) -> None:
        """Instantly reset gain without smoothing."""
        self._gain.reset(db_to_linear(gain_db))

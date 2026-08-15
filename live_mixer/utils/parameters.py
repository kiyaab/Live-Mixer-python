"""Thread-safe parameter utilities for control/audio thread communication."""

from __future__ import annotations

import math
from dataclasses import dataclass
from threading import Lock
from typing import Optional


def db_to_linear(db: float) -> float:
    """Convert decibels to linear amplitude."""
    return 10.0 ** (db / 20.0)


def linear_to_db(linear: float, floor_db: float = -120.0) -> float:
    """Convert linear amplitude to decibels."""
    if linear <= 0.0:
        return floor_db
    return 20.0 * math.log10(linear)


@dataclass
class SmoothParameter:
    """
    Exponential parameter smoother safe for real-time audio processing.

    Control thread sets target values; audio thread reads smoothed values
    without blocking locks.
    """

    value: float
    target: float
    smoothing_coeff: float = 0.05

    def set_target(self, target: float) -> None:
        """Set the target value from the control thread."""
        self.target = target

    def process(self, num_samples: int) -> float:
        """
        Advance smoothing by num_samples and return current value.

        Uses per-sample exponential smoothing inside the block.
        """
        coeff = self.smoothing_coeff
        current = self.value
        target = self.target
        for _ in range(num_samples):
            current += coeff * (target - current)
        self.value = current
        return current

    def process_block(self, num_samples: int) -> "np.ndarray":
        """Return a block of smoothed gain values (for per-sample gain ramps)."""
        import numpy as np

        coeff = self.smoothing_coeff
        current = self.value
        target = self.target
        block = np.empty(num_samples, dtype=np.float32)
        for i in range(num_samples):
            current += coeff * (target - current)
            block[i] = current
        self.value = current
        return block

    def reset(self, value: float) -> None:
        """Instantly set value and target."""
        self.value = value
        self.target = value

    @property
    def is_settled(self) -> bool:
        """True when smoothed value is close to target."""
        return abs(self.value - self.target) < 1e-6


class AtomicFloat:
    """Lock-protected float for meter/control data transfer."""

    def __init__(self, initial: float = 0.0) -> None:
        self._value = initial
        self._lock = Lock()

    def set(self, value: float) -> None:
        with self._lock:
            self._value = value

    def get(self) -> float:
        with self._lock:
            return self._value


class ParameterBank:
    """Named parameter store with thread-safe writes and snapshot reads."""

    def __init__(self) -> None:
        self._params: dict[str, float] = {}
        self._lock = Lock()

    def set(self, name: str, value: float) -> None:
        with self._lock:
            self._params[name] = value

    def get(self, name: str, default: float = 0.0) -> float:
        with self._lock:
            return self._params.get(name, default)

    def snapshot(self) -> dict[str, float]:
        with self._lock:
            return dict(self._params)

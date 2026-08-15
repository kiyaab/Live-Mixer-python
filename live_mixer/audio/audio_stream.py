"""PortAudio stream wrapper via sounddevice."""

from __future__ import annotations

import threading
from dataclasses import dataclass
from typing import Callable, Optional

import numpy as np
import sounddevice as sd


AudioCallback = Callable[[np.ndarray, int], np.ndarray]


@dataclass
class StreamConfig:
    """Configuration for an audio stream."""

    sample_rate: int = 48000
    block_size: int = 128
    input_channels: int = 4
    output_channels: int = 2
    input_device: Optional[int] = None
    output_device: Optional[int] = None
    dtype: str = "float32"


@dataclass
class StreamStats:
    """Performance statistics collected outside the callback."""

    callback_count: int = 0
    underruns: int = 0
    overruns: int = 0
    last_callback_us: float = 0.0
    max_callback_us: float = 0.0
    avg_callback_us: float = 0.0


class AudioStream:
    """
    Manages a duplex PortAudio stream.

    The process callback is invoked from PortAudio's real-time thread.
    Statistics are transferred via a lock-free counter pattern.
    """

    def __init__(self, config: StreamConfig, process_fn: AudioCallback) -> None:
        self.config = config
        self._process_fn = process_fn
        self._stream: Optional[sd.Stream] = None
        self._running = False
        self._stats = StreamStats()
        self._stats_lock = threading.Lock()
        self._callback_times: list[float] = []
        self._max_callback_history = 100

    @property
    def is_running(self) -> bool:
        return self._running

    @property
    def stats(self) -> StreamStats:
        with self._stats_lock:
            return StreamStats(
                callback_count=self._stats.callback_count,
                underruns=self._stats.underruns,
                overruns=self._stats.overruns,
                last_callback_us=self._stats.last_callback_us,
                max_callback_us=self._stats.max_callback_us,
                avg_callback_us=self._stats.avg_callback_us,
            )

    def start(self) -> None:
        """Start the duplex audio stream."""
        if self._running:
            return

        def callback(indata, outdata, frames, time_info, status) -> None:
            import time

            t0 = time.perf_counter()
            try:
                if status.input_underflow:
                    self._increment_underruns()
                if status.output_underflow:
                    self._increment_underruns()
                if status.input_overflow:
                    self._increment_overruns()
                if status.output_overflow:
                    self._increment_overruns()

                result = self._process_fn(indata, frames)
                outdata[:frames] = result[:frames]
            except Exception:
                outdata[:frames].fill(0.0)
            finally:
                elapsed_us = (time.perf_counter() - t0) * 1_000_000
                self._record_callback_time(elapsed_us)

        self._stream = sd.Stream(
            samplerate=self.config.sample_rate,
            blocksize=self.config.block_size,
            device=(self.config.input_device, self.config.output_device),
            channels=(self.config.input_channels, self.config.output_channels),
            dtype=self.config.dtype,
            callback=callback,
        )
        self._stream.start()
        self._running = True

    def stop(self) -> None:
        """Stop and close the stream."""
        if self._stream is not None:
            self._stream.stop()
            self._stream.close()
            self._stream = None
        self._running = False

    def _increment_underruns(self) -> None:
        with self._stats_lock:
            self._stats.underruns += 1

    def _increment_overruns(self) -> None:
        with self._stats_lock:
            self._stats.overruns += 1

    def _record_callback_time(self, elapsed_us: float) -> None:
        with self._stats_lock:
            self._stats.callback_count += 1
            self._stats.last_callback_us = elapsed_us
            if elapsed_us > self._stats.max_callback_us:
                self._stats.max_callback_us = elapsed_us
            self._callback_times.append(elapsed_us)
            if len(self._callback_times) > self._max_callback_history:
                self._callback_times.pop(0)
            self._stats.avg_callback_us = sum(self._callback_times) / len(
                self._callback_times
            )

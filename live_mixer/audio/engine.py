"""Real-time audio engine — orchestrates I/O, mixing, and master output."""

from __future__ import annotations

import threading
import time
from dataclasses import dataclass, field
from typing import Optional

import numpy as np

from audio.audio_stream import AudioStream, StreamConfig, StreamStats
from audio.buffer_manager import BufferManager
from audio.channel import ChannelState
from audio.device_manager import DeviceManager
from audio.master import MasterSection
from audio.mixer import Mixer


@dataclass
class EngineConfig:
    """Engine configuration."""

    sample_rate: int = 48000
    block_size: int = 128
    num_channels: int = 4
    input_device: Optional[int] = None
    output_device: Optional[int] = None
    master_gain_db: float = 0.0


@dataclass
class EngineStatus:
    """Status snapshot for GUI/monitoring."""

    running: bool = False
    sample_rate: int = 48000
    block_size: int = 128
    num_channels: int = 4
    cpu_percent: float = 0.0
    estimated_latency_ms: float = 0.0
    stream_stats: StreamStats = field(default_factory=StreamStats)


class AudioEngine:
    """
    Central real-time audio engine.

    Owns the mixer, master section, buffers, and stream.
    Control thread modifies parameters; audio callback reads them.
    """

    def __init__(
        self,
        config: EngineConfig,
        device_manager: Optional[DeviceManager] = None,
    ) -> None:
        self.config = config
        self.device_manager = device_manager or DeviceManager()

        channel_names = [f"CH{i + 1}" for i in range(config.num_channels)]
        self.mixer = Mixer(
            num_channels=config.num_channels,
            sample_rate=config.sample_rate,
            channel_names=channel_names,
        )
        self.master = MasterSection(
            gain_db=config.master_gain_db,
            sample_rate=config.sample_rate,
        )
        self.buffers = BufferManager(
            max_block_size=config.block_size,
            num_input_channels=config.num_channels,
            num_output_channels=2,
        )
        self._stream: Optional[AudioStream] = None
        self._running = False
        self._error: Optional[str] = None
        self._cpu_percent = 0.0

    @property
    def is_running(self) -> bool:
        return self._running

    @property
    def last_error(self) -> Optional[str]:
        return self._error

    def start(self) -> None:
        """Start the audio engine."""
        if self._running:
            return

        try:
            in_dev, out_dev = self.device_manager.resolve_devices(
                self.config.input_device,
                self.config.output_device,
            )
        except RuntimeError as exc:
            self._error = str(exc)
            raise

        stream_config = StreamConfig(
            sample_rate=self.config.sample_rate,
            block_size=self.config.block_size,
            input_channels=self.config.num_channels,
            output_channels=2,
            input_device=in_dev,
            output_device=out_dev,
        )

        self._stream = AudioStream(stream_config, self._audio_callback)
        try:
            self._stream.start()
            self._running = True
            self._error = None
        except Exception as exc:
            self._error = str(exc)
            self._stream = None
            raise

    def stop(self) -> None:
        """Stop the audio engine."""
        if self._stream is not None:
            self._stream.stop()
            self._stream = None
        self._running = False

    def _audio_callback(self, indata: np.ndarray, num_frames: int) -> np.ndarray:
        """
        Real-time audio callback.

        NO allocations, logging, file I/O, or blocking operations here.
        """
        np.copyto(self.buffers.input_buffer[:num_frames], indata)

        self.mixer.process(
            self.buffers.input_buffer,
            self.buffers.mix_left,
            self.buffers.mix_right,
            num_frames,
        )

        self.master.process(
            self.buffers.mix_left,
            self.buffers.mix_right,
            self.buffers.output_buffer,
            num_frames,
        )

        block_duration = num_frames / self.config.sample_rate
        if self._stream is not None:
            stats = self._stream.stats
            if stats.last_callback_us > 0:
                self._cpu_percent = min(
                    100.0,
                    (stats.last_callback_us / 1_000_000) / block_duration * 100.0,
                )

        return self.buffers.output_buffer[:num_frames]

    # --- Control interface ---

    def set_master_gain(self, gain_db: float) -> None:
        self.master.set_gain_db(gain_db)

    def set_channel_gain(self, channel: int, gain_db: float) -> None:
        self.mixer.set_channel_gain(channel, gain_db)

    def set_channel_fader(self, channel: int, fader_db: float) -> None:
        self.mixer.set_channel_fader(channel, fader_db)

    def set_channel_pan(self, channel: int, pan: float) -> None:
        self.mixer.set_channel_pan(channel, pan)

    def set_channel_mute(self, channel: int, muted: bool) -> None:
        self.mixer.set_channel_mute(channel, muted)

    def set_channel_solo(self, channel: int, soloed: bool) -> None:
        self.mixer.set_channel_solo(channel, soloed)

    def get_status(self) -> EngineStatus:
        """Return engine status for monitoring/GUI."""
        latency_ms = (
            self.config.block_size * 2 / self.config.sample_rate * 1000.0
        )
        stats = self._stream.stats if self._stream else StreamStats()
        return EngineStatus(
            running=self._running,
            sample_rate=self.config.sample_rate,
            block_size=self.config.block_size,
            num_channels=self.config.num_channels,
            cpu_percent=self._cpu_percent,
            estimated_latency_ms=latency_ms,
            stream_stats=stats,
        )

    def get_meter_levels(self) -> dict:
        """Return current meter readings for all channels and master."""
        return {
            "channels": [
                {
                    "peak": ch.meter_state.peak,
                    "rms": ch.meter_state.rms,
                    "peak_hold": ch.meter_state.peak_hold,
                    "clipped": ch.meter_state.clipped,
                }
                for ch in self.mixer.channels
            ],
            "master": {
                "peak": self.master.meter_state.peak,
                "rms": self.master.meter_state.rms,
                "peak_hold": self.master.meter_state.peak_hold,
                "clipped": self.master.meter_state.clipped,
            },
            "main_bus": {
                "peak": self.mixer.main_bus.meter_state.peak,
                "rms": self.mixer.main_bus.meter_state.rms,
            },
        }

"""Multi-channel mixer with routing and bus summing."""

from __future__ import annotations

from typing import Optional

import numpy as np

from audio.bus import Bus, BusType
from audio.channel import Channel, ChannelState
from audio.routing import RouteDestination, RoutingEngine


class Mixer:
    """
    Combines channels, applies routing, and produces stereo main mix.

    Real-time safe: uses preallocated buffers passed from BufferManager.
    """

    def __init__(
        self,
        num_channels: int = 4,
        sample_rate: int = 48000,
        channel_names: Optional[list[str]] = None,
    ) -> None:
        names = channel_names or [f"CH{i + 1}" for i in range(num_channels)]
        self.channels: list[Channel] = [
            Channel(name=names[i], sample_rate=sample_rate)
            for i in range(num_channels)
        ]
        self.routing = RoutingEngine(num_channels)
        self.main_bus = Bus("Main", BusType.MAIN, sample_rate)
        self._any_solo = False

    @property
    def num_channels(self) -> int:
        return len(self.channels)

    def any_solo_active(self) -> bool:
        return any(ch.is_solo for ch in self.channels)

    def process(
        self,
        input_buffer: np.ndarray,
        mix_left: np.ndarray,
        mix_right: np.ndarray,
        num_frames: int,
    ) -> None:
        """
        Process all channels and sum to stereo mix buffers.

        Args:
            input_buffer: Input audio shape (frames, input_channels).
            mix_left: Preallocated left mix buffer.
            mix_right: Preallocated right mix buffer.
            num_frames: Block size.
        """
        mix_left[:num_frames].fill(0.0)
        mix_right[:num_frames].fill(0.0)

        any_solo = self.any_solo_active()

        for i, channel in enumerate(self.channels):
            input_idx = self.routing.get_input_for_channel(i)
            if input_idx >= input_buffer.shape[1]:
                continue

            mono_in = input_buffer[:num_frames, input_idx]
            left, right = channel.process(mono_in, num_frames, any_solo, any_solo)

            if self.routing.is_routed_to(i, RouteDestination.MAIN):
                mix_left[:num_frames] += left
                mix_right[:num_frames] += right

        self.main_bus.update_meter(mix_left, mix_right, num_frames)

    def get_channel(self, index: int) -> Channel:
        return self.channels[index]

    def set_channel_gain(self, index: int, gain_db: float) -> None:
        self.channels[index].set_gain(gain_db)

    def set_channel_fader(self, index: int, fader_db: float) -> None:
        self.channels[index].set_fader(fader_db)

    def set_channel_pan(self, index: int, pan: float) -> None:
        self.channels[index].set_pan(pan)

    def set_channel_mute(self, index: int, muted: bool) -> None:
        self.channels[index].mute(muted)

    def set_channel_solo(self, index: int, soloed: bool) -> None:
        self.channels[index].solo(soloed)

    def apply_channel_states(self, states: list[ChannelState]) -> None:
        for i, state in enumerate(states):
            if i < len(self.channels):
                self.channels[i].apply_state(state)

    def get_channel_states(self) -> list[ChannelState]:
        return [ch.get_state() for ch in self.channels]

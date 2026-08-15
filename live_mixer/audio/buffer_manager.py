"""Preallocated buffer pool for real-time audio processing."""

from __future__ import annotations

import numpy as np


class BufferManager:
    """
    Manages preallocated numpy buffers to avoid allocations in the audio callback.

    All buffers are float32 and reused across processing blocks.
    """

    def __init__(
        self,
        max_block_size: int,
        num_input_channels: int,
        num_output_channels: int = 2,
    ) -> None:
        self.max_block_size = max_block_size
        self.num_input_channels = num_input_channels
        self.num_output_channels = num_output_channels

        self.input_buffer = np.zeros(
            (max_block_size, num_input_channels), dtype=np.float32
        )
        self.channel_buffer = np.zeros(max_block_size, dtype=np.float32)
        self.mix_left = np.zeros(max_block_size, dtype=np.float32)
        self.mix_right = np.zeros(max_block_size, dtype=np.float32)
        self.output_buffer = np.zeros(
            (max_block_size, num_output_channels), dtype=np.float32
        )

    def resize(self, block_size: int, num_input_channels: int) -> None:
        """Reallocate buffers when block size or channel count changes."""
        if (
            block_size <= self.max_block_size
            and num_input_channels <= self.num_input_channels
        ):
            return
        self.max_block_size = max(block_size, self.max_block_size)
        self.num_input_channels = max(num_input_channels, self.num_input_channels)
        self.__init__(
            self.max_block_size,
            self.num_input_channels,
            self.num_output_channels,
        )

    def clear_mix_buffers(self, num_frames: int) -> None:
        """Zero mix buffers for the current block."""
        self.mix_left[:num_frames].fill(0.0)
        self.mix_right[:num_frames].fill(0.0)

    def clear_output(self, num_frames: int) -> None:
        """Zero output buffer for the current block."""
        self.output_buffer[:num_frames].fill(0.0)

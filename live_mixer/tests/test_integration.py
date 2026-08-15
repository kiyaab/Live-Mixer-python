"""Integration test for offline audio pipeline."""

import numpy as np

from audio.buffer_manager import BufferManager
from audio.engine import AudioEngine, EngineConfig
from audio.master import MasterSection
from audio.mixer import Mixer


class TestOfflinePipeline:
    """Simulate the audio callback without PortAudio."""

    def test_sine_wave_passthrough(self):
        sample_rate = 48000
        num_frames = 256
        num_channels = 2

        mixer = Mixer(num_channels=num_channels, sample_rate=sample_rate)
        master = MasterSection(sample_rate=sample_rate)
        buffers = BufferManager(num_frames, num_channels)

        for ch in mixer.channels:
            ch.input_gain._gain.reset(1.0)
            ch.fader._gain.reset(1.0)
        master.gain._gain.reset(1.0)

        t = np.arange(num_frames, dtype=np.float32) / sample_rate
        sine = (0.5 * np.sin(2 * np.pi * 440 * t)).astype(np.float32)

        buffers.input_buffer[:num_frames, 0] = sine
        buffers.input_buffer[:num_frames, 1] = sine * 0.5

        mixer.process(
            buffers.input_buffer,
            buffers.mix_left,
            buffers.mix_right,
            num_frames,
        )
        master.process(
            buffers.mix_left,
            buffers.mix_right,
            buffers.output_buffer,
            num_frames,
        )

        output = buffers.output_buffer[:num_frames]
        assert output.shape == (num_frames, 2)
        assert np.max(np.abs(output)) > 0.1
        assert np.max(np.abs(output)) < 1.0

    def test_engine_config_defaults(self):
        config = EngineConfig()
        assert config.sample_rate == 48000
        assert config.block_size == 128
        assert config.num_channels == 4

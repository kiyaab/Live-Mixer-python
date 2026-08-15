"""Tests for mixer channel processing."""

import numpy as np
import pytest

from audio.channel import Channel, pan_to_stereo_gains
from audio.mixer import Mixer


class TestPanLaw:
    def test_center(self):
        left, right = pan_to_stereo_gains(0.0)
        assert left == pytest.approx(right, rel=0.01)
        assert left == pytest.approx(0.707, rel=0.01)

    def test_full_left(self):
        left, right = pan_to_stereo_gains(-1.0)
        assert left == pytest.approx(1.0, abs=0.01)
        assert right == pytest.approx(0.0, abs=0.01)

    def test_full_right(self):
        left, right = pan_to_stereo_gains(1.0)
        assert left == pytest.approx(0.0, abs=0.01)
        assert right == pytest.approx(1.0, abs=0.01)


class TestChannel:
    def test_unity_passthrough(self):
        ch = Channel("CH1")
        ch.input_gain._gain.reset(1.0)
        ch.fader._gain.reset(1.0)
        audio = np.ones(64, dtype=np.float32) * 0.5
        left, right = ch.process(audio, 64, False, False)
        assert left[0] == pytest.approx(0.354, rel=0.01)
        assert right[0] == pytest.approx(0.354, rel=0.01)

    def test_mute_silences_output(self):
        ch = Channel("CH1")
        ch.input_gain._gain.reset(1.0)
        ch.fader._gain.reset(1.0)
        ch.mute(True)
        audio = np.ones(64, dtype=np.float32)
        left, right = ch.process(audio, 64, False, False)
        assert np.max(np.abs(left)) == 0.0
        assert np.max(np.abs(right)) == 0.0

    def test_solo_logic(self):
        ch = Channel("CH1")
        ch.input_gain._gain.reset(1.0)
        ch.fader._gain.reset(1.0)
        ch.solo(True)
        audio = np.ones(64, dtype=np.float32) * 0.5
        left, right = ch.process(audio, 64, True, True)
        assert left[0] > 0.0


class TestMixer:
    def test_channel_summation(self):
        mixer = Mixer(num_channels=2)
        for ch in mixer.channels:
            ch.input_gain._gain.reset(1.0)
            ch.fader._gain.reset(1.0)

        num_frames = 64
        input_buf = np.zeros((num_frames, 2), dtype=np.float32)
        input_buf[:, 0] = 0.5
        input_buf[:, 1] = 0.3

        mix_l = np.zeros(num_frames, dtype=np.float32)
        mix_r = np.zeros(num_frames, dtype=np.float32)
        mixer.process(input_buf, mix_l, mix_r, num_frames)

        assert mix_l[0] > 0.0
        assert mix_r[0] > 0.0

    def test_solo_mutes_non_solo_channels(self):
        mixer = Mixer(num_channels=2)
        for ch in mixer.channels:
            ch.input_gain._gain.reset(1.0)
            ch.fader._gain.reset(1.0)
        mixer.channels[0].solo(True)

        num_frames = 64
        input_buf = np.ones((num_frames, 2), dtype=np.float32) * 0.5
        mix_l = np.zeros(num_frames, dtype=np.float32)
        mix_r = np.zeros(num_frames, dtype=np.float32)
        mixer.process(input_buf, mix_l, mix_r, num_frames)

        ch1_only = mix_l[0]
        mixer.channels[0].solo(False)
        mixer.process(input_buf, mix_l, mix_r, num_frames)
        both = mix_l[0]
        assert both > ch1_only

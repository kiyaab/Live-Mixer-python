"""Tests for gain DSP module."""

import numpy as np
import pytest

from audio.dsp.gain import Gain
from utils.parameters import db_to_linear, linear_to_db


class TestDbConversion:
    def test_unity_gain(self):
        assert db_to_linear(0.0) == pytest.approx(1.0)

    def test_negative_6db(self):
        assert db_to_linear(-6.0) == pytest.approx(0.501, rel=0.01)

    def test_linear_to_db_unity(self):
        assert linear_to_db(1.0) == pytest.approx(0.0)

    def test_linear_to_db_silence(self):
        assert linear_to_db(0.0) == -120.0


class TestGain:
    def test_unity_gain_passthrough(self):
        gain = Gain(0.0)
        gain._gain.reset(1.0)
        audio = np.ones(128, dtype=np.float32) * 0.5
        result = gain.process(audio)
        np.testing.assert_allclose(result, 0.5, rtol=1e-5)

    def test_silence_at_minus_inf(self):
        gain = Gain(-120.0)
        gain._gain.reset(db_to_linear(-120.0))
        audio = np.ones(64, dtype=np.float32)
        result = gain.process(audio)
        assert np.max(np.abs(result)) < 1e-5

    def test_gain_doubling(self):
        gain = Gain(6.0)
        gain._gain.reset(db_to_linear(6.0))
        audio = np.ones(64, dtype=np.float32) * 0.25
        result = gain.process(audio)
        np.testing.assert_allclose(result, 0.5, rtol=0.01)

    def test_smooth_gain_change(self):
        gain = Gain(0.0)
        gain._gain.reset(1.0)
        audio = np.ones(256, dtype=np.float32)
        gain.set_gain_db(-20.0)
        result = gain.process(audio)
        assert result[0] == pytest.approx(1.0, abs=0.1)
        assert result[-1] < result[0]

    def test_stereo_processing(self):
        gain = Gain(0.0)
        gain._gain.reset(1.0)
        audio = np.ones((64, 2), dtype=np.float32) * 0.3
        result = gain.process(audio)
        assert result.shape == (64, 2)
        np.testing.assert_allclose(result, 0.3, rtol=1e-5)

    def test_in_place_output(self):
        gain = Gain(0.0)
        gain._gain.reset(1.0)
        audio = np.ones(32, dtype=np.float32) * 0.7
        out = np.zeros(32, dtype=np.float32)
        result = gain.process(audio, out=out)
        assert result is out
        np.testing.assert_allclose(out, 0.7, rtol=1e-5)

"""Tests for metering."""

import numpy as np
import pytest

from audio.dsp.metering import PeakRMSMeter


class TestPeakRMSMeter:
    def test_silence(self):
        meter = PeakRMSMeter()
        audio = np.zeros(128, dtype=np.float32)
        state = meter.process(audio)
        assert state.peak == 0.0
        assert state.rms == 0.0
        assert not state.clipped

    def test_peak_detection(self):
        meter = PeakRMSMeter()
        audio = np.zeros(64, dtype=np.float32)
        audio[10] = 0.8
        state = meter.process(audio)
        assert state.peak == pytest.approx(0.8)

    def test_clip_detection(self):
        meter = PeakRMSMeter()
        audio = np.ones(32, dtype=np.float32) * 1.0
        state = meter.process(audio)
        assert state.clipped

    def test_stereo_metering(self):
        meter = PeakRMSMeter()
        audio = np.zeros((64, 2), dtype=np.float32)
        audio[:, 1] = 0.6
        state = meter.process(audio)
        assert state.peak == pytest.approx(0.6)

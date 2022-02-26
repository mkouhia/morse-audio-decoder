"""Test audio signal processing"""

import numpy as np
from numpy.testing import assert_array_equal, assert_array_almost_equal
import pytest

from morse_audio_decoder.processing import smoothed_power


@pytest.fixture(name="data")
def data_fx() -> np.ndarray:
    """Create sample data (1 second of 600 Hz sine wave)"""
    return (np.sin(np.linspace(0, 600 * np.pi * 2, 44100)) * (2**15 - 1)).astype(
        np.int16
    )


def test_smoothed_power_rms(data: np.ndarray):
    """Test that RMS value is almost equal to peak/sqrt(2)

    It will not be exactly equal, as Hann window smoothing retains some ripple
    """
    received = smoothed_power(data, 44100 // 600 * 4)
    expected = (
        np.ones(len(data) - 44100 // 600 * 4 + 1) / np.sqrt(2) * (2**15 - 1)
    ).astype(np.int16)

    assert_array_equal(received // 100, expected // 100)


def test_smoothed_power_rms_float():
    """Test that RMS of sine wave is almost 1/sqrt(2)

    It will not be exactly equal, as Hann window smoothing retains some ripple
    """
    data = np.sin(np.linspace(0, 600 * np.pi * 2, 44100))

    received = smoothed_power(data, 44100 // 600 * 4)
    expected = np.ones(len(data) - 44100 // 600 * 4 + 1) / np.sqrt(2)

    assert_array_almost_equal(received, expected, 3)


def test_smoothed_power_dtype(data):
    """Output dtype is int16 for int16 input"""
    received = smoothed_power(data, 44100 // 600)

    assert received.dtype == data.dtype


def test_smoothed_power_same(data):
    """Window length is equal to input length"""
    received = smoothed_power(data, 44100 // 600, mode="same")

    assert received.size == data.size

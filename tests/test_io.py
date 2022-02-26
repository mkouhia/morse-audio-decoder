"""Test input/output"""

from pathlib import Path

import numpy as np

from morse_audio_decoder.io import read_wave
from .common_fixtures import wav_file_fx  # pylint: disable=unused-import


def test_read_wave_frame_rate(wav_file: Path):
    """Expect 44100 Hz frame rate"""
    frame_rate, _ = read_wave(wav_file)
    assert frame_rate == 44100


def test_read_wave_shape(wav_file: Path):
    """Expect 1D data for mono audio"""
    _, data = read_wave(wav_file)
    assert len(data.shape) == 1


def test_read_wave_dtype(wav_file: Path):
    """Expect 16 bit integer array"""
    _, data = read_wave(wav_file)
    assert data.dtype == np.int16

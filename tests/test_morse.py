"""Test morse code handling"""

from pathlib import Path

import numpy as np
import pytest

from morse_audio_decoder.morse import MorseCode
from .common_fixtures import wav_file_fx  # pylint: disable=unused-import


@pytest.fixture(name="hello_data")
def hello_data_fx() -> np.ndarray:
    """Add dummy data for HELLO WORLD string"""
    hello_world_str = "|.... . .-.. .-.. ---|.-- --- .-. .-.. -..|"
    hello_world_str = (
        hello_world_str.replace(" ", "00")
        .replace("|", "000000")
        .replace(".", "10")
        .replace("-", "1110")
    )
    return np.repeat(np.array([int(i) for i in hello_world_str]), 44100 * 60 // 1000)


def test_from_wavfile(wav_file: Path):
    """Constructor runs and data is initalized with something"""
    received = MorseCode.from_wavfile(wav_file)

    assert len(received.data) > 0


@pytest.mark.skip("Not implemented")
def test_decode(hello_data: np.ndarray):
    """Dummy data decoding works"""
    received = MorseCode(hello_data).decode()
    assert received == "HELLO WORLD"


def test_morse_to_char():
    """All alphanumeric characters and full stop are in values"""
    received = MorseCode(np.empty(1)).morse_to_char
    expected_chars = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ."

    assert set(received.values()).issuperset(expected_chars)


def test_morse_to_char_cached():
    """Cached dictionary is read from MorseCode._morse_to_char"""
    morse = MorseCode(np.empty(1))
    expected = {"..": "A"}
    MorseCode._morse_to_char = expected  # pylint: disable=protected-access

    received = morse.morse_to_char

    assert received == expected

"""Test morse code handling"""

from pathlib import Path

import numpy as np
import pytest

from morse_audio_decoder.morse import MorseCode

# pylint: disable=unused-import
from .common_fixtures import (
    wav_file_fx,
    wav_file_8bit_fx,
)


@pytest.fixture(name="hello_world_morse")
def hello_world_morse_fx() -> str:
    """HELLO WORLD string in morse"""
    return ".... . .-.. .-.. ---|.-- --- .-. .-.. -.."


@pytest.fixture(name="hello_data")
def hello_data_fx(hello_world_morse: str) -> np.ndarray:
    """Add dummy data for HELLO WORLD string"""
    hello_world_str = (
        "000"
        + (
            hello_world_morse.replace(" ", "00")
            .replace("|", "000000")
            .replace(".", "10")
            .replace("-", "1110")
        )
        + "00"
    )
    return np.repeat(np.array([int(i) for i in hello_world_str]), 44100 * 60 // 1000)


def test_from_wavfile(wav_file: Path):
    """Constructor runs and data is initalized with something"""
    received = MorseCode.from_wavfile(wav_file)

    assert len(received.data) > 0


def test_from_wavfile_8bit(wav_file_8bit: Path):
    """Construction with 8bit input data also works"""
    received = MorseCode.from_wavfile(wav_file_8bit)

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


def test_morse_to_char_cached(mocker):
    """Cached dictionary is read from MorseCode._morse_to_char"""
    expected = {"..": "A"}
    mocker.patch("morse_audio_decoder.morse.MorseCode._morse_to_char", expected)
    morse = MorseCode(np.empty(1))

    received = morse.morse_to_char

    assert received == expected


def test_morse_words(hello_world_morse: str):
    """Expansion of character and space arrays works as expected"""
    only_dash_dots = hello_world_morse.replace("|", "").replace(" ", "")
    dash_dot_characters = np.array(list(only_dash_dots))

    all_same_spaces = hello_world_morse.replace("|", " ")
    any_space_idx = np.nonzero(np.array(list(all_same_spaces)) == " ")[0]
    any_space_idx = any_space_idx - np.arange(len(any_space_idx))

    word_space_idx = np.nonzero(np.array(list("HELLO WORLD")) == " ")[0]

    # pylint: disable=protected-access
    received = MorseCode(np.zeros(10))._morse_words(
        dash_dot_characters, any_space_idx, word_space_idx
    )
    expected = [word.split(" ") for word in hello_world_morse.split("|")]

    assert received == expected


def test_translate(hello_world_morse: str):
    """Correct translation is received"""
    morse_words = [word.split(" ") for word in hello_world_morse.split("|")]

    # pylint: disable=protected-access
    received = MorseCode(np.zeros(10))._translate(morse_words)
    expected = "HELLO WORLD"

    assert received == expected

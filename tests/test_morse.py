"""Test morse code handling"""

from pathlib import Path

from morse_audio_decoder.morse import MorseCode
from .common_fixtures import wav_file_fx  # pylint: disable=unused-import


def test_from_wavfile(wav_file: Path):
    """Constructor runs and data is initalized with something"""
    received = MorseCode.from_wavfile(wav_file)

    assert len(received.data) > 0

"""Main tests"""

from argparse import ArgumentParser
import numpy as np
from morse_audio_decoder import __version__
from morse_audio_decoder.__main__ import main, parse_args


def test_version():
    """Check that version is not accidentally changed

    Make sure to update this test whenever release is made
    """
    assert __version__ == "0.0.1"


def test_main(mocker):
    """MorseCode instance is created and decode is called"""

    expected = "HELLO TEST"

    # pylint: disable=all
    class TestClass:
        def __init__(self, data):
            self.data = data

        def decode(self):
            return "HELLO TEST"

        @classmethod
        def from_wavfile(cls, file):
            return cls(np.array([0, 1]))

    mocker.patch("morse_audio_decoder.__main__.MorseCode", TestClass)

    parser = ArgumentParser()
    parser.add_argument("WAVFILE")
    args = parser.parse_args(["file.wav"])
    print(args)
    received = main(args)
    assert received == expected


def test_parser_wavfile():
    """Argument parser receives filename"""
    test_filename = "test_file"
    parser = parse_args([test_filename])

    assert parser.WAVFILE == test_filename

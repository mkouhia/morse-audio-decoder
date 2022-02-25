"""Main tests"""

from morse_audio_decoder import __version__
from morse_audio_decoder.__main__ import parse_args


def test_version():
    """Check that version is not accidentally changed

    Make sure to update this test whenever release is made
    """
    assert __version__ == "0.0.1"


def test_parser_wavfile():
    """Argument parser receives filename"""
    test_filename = "test_file"
    parser = parse_args([test_filename])

    assert parser.WAVFILE == test_filename

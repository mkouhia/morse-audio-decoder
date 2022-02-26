"""Morse code handling"""

from configparser import ConfigParser
import os
from pathlib import Path

import numpy as np

from .io import read_wave
from .processing import smoothed_power, squared_signal


class MorseCode:

    """Morse code

    Attributes:
        data (np.ndarray): 1D binary array, representing morse code in time
    """

    _morse_to_char: dict = None

    def __init__(self, data: np.ndarray):
        """Initialize code with binary data

        Args:
            data (np.ndarray): 1D binary array, representing morse code in time
        """
        self.data = data

    @classmethod
    def from_wavfile(cls, file: os.PathLike) -> "MorseCode":
        """Construct from wave file

        - Read in wave file
        - Calculate signal envelope (smoothing of 0.1 seconds)
        - Apply squaring (threshold: 50% of max smoothed data value)

        Args:
            file (os.PathLike): path to input WAV file

        Returns:
            MorseCode: class instance, with 1D binary input data
        """
        sample_rate, wave = read_wave(file)
        window_size = int(0.01 * sample_rate)
        envelope = smoothed_power(wave, window_size)
        square_data = squared_signal(envelope)

        return cls(square_data)

    def decode(self) -> str:
        """Decode data

        Returns:
            str: Morse code content, in plain language
        """
        raise NotImplementedError()

    @classmethod
    @property
    def morse_to_char(cls) -> dict[str, str]:
        """Morse to character dictionary

        Read mappings from morse.ini and store them to class variable. Later,
        return directly from this class variable.

        Returns:
            dict[str, str]: Mapping of morse character string to letter
        """
        if cls._morse_to_char is not None:
            return cls._morse_to_char

        config = ConfigParser()
        config.read(Path(__file__).parent / "morse.ini")
        chars = config["characters"]
        cls._morse_to_char = {chars[key]: key.upper() for key in chars}
        return cls._morse_to_char

    def _translate(self, morse_words: list[list[str]]) -> str:
        """Translate list of morse-coded words to string

        Args:
            morse_words (list[list[str]]): List of words, having list of characters.
                The characters are in morse-coded dash/dot form, e.g. '.--' for 'w'

        Returns:
            str: Message contained in input
        """
        char_dict = self.morse_to_char
        char_lists = [[char_dict.get(j) for j in i] for i in morse_words]
        return " ".join(["".join(word) for word in char_lists])

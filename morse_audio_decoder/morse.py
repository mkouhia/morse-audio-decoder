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

    @staticmethod
    def _morse_words(
        raw_dash_dot: np.ndarray,
        char_break_idx: np.ndarray,
        word_space_idx: np.ndarray,
    ) -> list[list[str]]:
        """Convert character and space arrays to list of morse words

        Args:
            raw_dash_dot (np.ndarray): Numpy array of strings, contains
                '.' and '-' characters, as processed from self.data
            char_break_idx (np.ndarray): Index of locations in raw_dash_dot,
                where a character space or word space would exist. The array
                raw_dash_dot is first broken into characters with this index.
            word_space_idx (np.ndarray): Index for breaking character array
                into words. Contains locations of word spaces between natural
                language characters.

        Returns:
            list[list[str]]: Words in morse code. A single word is a list of
                dash-dot character combinations.
        """

        char_start_idx = [0] + (char_break_idx).tolist()
        char_end_idx = (char_break_idx).tolist() + [len(raw_dash_dot)]
        morse_characters = [
            "".join(raw_dash_dot[i:j].tolist())
            for i, j in zip(char_start_idx, char_end_idx)
        ]

        word_start_idx = [0] + (word_space_idx).tolist()
        word_end_idx = (word_space_idx).tolist() + [len(morse_characters)]

        return [morse_characters[i:j] for i, j in zip(word_start_idx, word_end_idx)]

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

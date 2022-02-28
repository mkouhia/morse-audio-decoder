"""Morse code handling"""

from configparser import ConfigParser
import os
from pathlib import Path

import numpy as np
from sklearn.cluster import KMeans

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

    def _on_off_samples(self) -> tuple[np.ndarray, np.ndarray]:
        """Calculate signal ON/OFF durations

        Locate rising and falling edges in square wave at self.data. Calculate
        number of samples in each ON / OFF period.

        Returns:
            tuple[np.ndarray, np.ndarray]: on_samples, off_samples. Note that
                in addition to character and word spaces, off_samples also
                includes inter-character spaces.
        """
        square_diff = np.diff(self.data)

        rising_idx = np.nonzero(square_diff == 1)[0]
        falling_idx = np.nonzero(square_diff == -1)[0]

        # Case: data starts with ON - it started one sample before index 0
        if falling_idx[0] < rising_idx[0]:
            rising_idx = np.insert(rising_idx, 0, -1)

        # Case: data ends with ON
        if rising_idx[-1] > falling_idx[-1]:
            falling_idx = np.insert(falling_idx, len(falling_idx), len(self.data) - 1)

        on_samples = falling_idx - rising_idx
        off_samples = rising_idx[1:] - falling_idx[: len(falling_idx) - 1]

        return on_samples, off_samples

    @staticmethod
    def _dash_dot_characters(on_samples: np.ndarray) -> np.ndarray:
        """Convert array of ON sample lengths to array of dashes and dots

        NOTE: It is expected, that the signal contains exactly two distinct
        lengths - those for a dash and for a dot. If the keying speed varies,
        or either character does not exist, then this method will fail.

        Args:
            on_samples (np.ndarray): number of samples in each ON period in
                the signal. This comes from `MorseCode._on_off_samples`.

        Returns:
            np.ndarray: array of dashes and dots, of object (string) type
        """
        column_vec = on_samples.reshape(-1, 1)
        clustering = KMeans(n_clusters=2, random_state=0).fit(column_vec)

        cluster_sort_idx = np.argsort(clustering.cluster_centers_.flatten()).tolist()
        dot_label = cluster_sort_idx.index(0)
        dash_label = cluster_sort_idx.index(1)

        dash_dot_map = {dot_label: ".", dash_label: "-"}
        dash_dot_characters = np.vectorize(dash_dot_map.get)(clustering.labels_)

        return dash_dot_characters

    @staticmethod
    def _break_spaces(off_samples: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
        """Convert array of OFF sample lengths to indices for char/word breaks

        NOTE: It is expected, that the signal contains exactly three distinct
        space lengths: inter-character space, character space and word space.
        If the keying speed varies, or word spaces do not exist, then this
        method will fail.

        Args:
            off_samples (np.ndarray): number of samples in each OFF period in
                the signal. This comes from `MorseCode._on_off_samples`.

        Returns:
            tuple[np.ndarray, np.ndarray]: indices for breaking dash/dot
                character array from `MorseCode._dash_dot_characters`. First
                array contains positions, where character breaks should be.
                Second array contains positions, where word spaces should be in
                the list of already resolved morse characters.
        """
        column_vec = off_samples.reshape(-1, 1)
        clustering = KMeans(n_clusters=3, random_state=0).fit(column_vec)

        cluster_sort_idx = np.argsort(clustering.cluster_centers_.flatten()).tolist()

        # This index breaks dashes/dots into characters
        intra_space_label = cluster_sort_idx.index(0)
        char_break_idx = np.nonzero(clustering.labels_ != intra_space_label)[0] + 1

        char_or_word_space_arr = clustering.labels_[
            clustering.labels_ != intra_space_label
        ]

        # This index breaks character list into word lists
        word_space_label = cluster_sort_idx.index(2)
        word_space_idx = np.nonzero(char_or_word_space_arr == word_space_label)[0] + 1

        return char_break_idx, word_space_idx

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

"""Morse code handling"""

import os
import numpy as np

from .io import read_wave
from .processing import smoothed_power, squared_signal


class MorseCode:

    """Morse code

    Attributes:
        data (np.ndarray): 1D binary array, representing morse code in time
    """

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

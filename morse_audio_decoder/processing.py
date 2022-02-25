"""Audio signal processing"""

import numpy as np


def smoothed_power(
    data: np.ndarray, window_size: int, mode: str = "valid"
) -> np.ndarray:
    """Calculate moving time window RMS power for a signal

    Produce amplitude envelope, which reperesents signal power over time.
    Power is calculated as RMS (root mean squared) value.
    The envelope is smoothed by Hann window convolution.

    Args:
        data (np.ndarray): Input data
        window_size (int): Smoothing window length, samples
        mode (str): Convolution mode, one of  "same" and "valid".
            When "same", return same length array as in input; when "valid",
            convolution is only given for signal points that fully overlap with
            the smoothing window. See np.convolve documentation
            for further explanation.

    Returns:
        np.ndarray: smoothed array
    """
    # Convert data in order to avoid truncation errors
    if np.issubdtype(data.dtype, np.integer):
        secure_data = data.astype(np.int32) if data.itemsize < 32 else data
    else:
        secure_data = data.astype(np.float32) if data.itemsize < 32 else data

    # Create window with integral=1 -> multiplication results in weighted average
    window = np.hanning(window_size)
    window = window / sum(window)

    squared = np.power(secure_data, 2)

    return np.sqrt(np.convolve(squared, window, mode)).astype(data.dtype)

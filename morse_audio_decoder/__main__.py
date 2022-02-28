"""Command line interface"""

import argparse
import os
from pathlib import Path
import sys

from morse_audio_decoder.morse import MorseCode


def main(file: os.PathLike) -> None:
    """Read WAV file, process it and write outputs to stdout

    Args:
        file (os.PathLike): path to WAV file

    Raises:
        UserWarning: If dash/dot separation cannot be made unambiguosly.
    """
    if not Path(file).exists():
        sys.stderr.write(f"File {file} not found, exiting.\n")
        sys.exit(1)

    decoded = MorseCode.from_wavfile(file).decode()
    sys.stdout.write(decoded + "\n")


def parse_args(args: list[str]) -> argparse.Namespace:
    """Parse arguments from command line"""
    parser = argparse.ArgumentParser(
        description="""Read audio file in WAV format, extract the morse code and
        write translated text into standard output."""
    )
    parser.add_argument("WAVFILE", help="Input audio file")
    return parser.parse_args(args)


if __name__ == "__main__":
    program_arguments = parse_args(sys.argv[1:])
    try:
        main(program_arguments.WAVFILE)
    except UserWarning as err:
        sys.stderr.write(f"{err}\n")
        sys.exit(1)

"""Command line interface"""

import argparse
import sys

from morse_audio_decoder.morse import MorseCode


def main(args: argparse.Namespace) -> None:
    """Read WAV file, process it and write outputs to stdout

    Args:
        args (argparse.Namespace): argparse arguments
    """
    return MorseCode.from_wavfile(args.WAVFILE).decode()


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
    main(*program_arguments)

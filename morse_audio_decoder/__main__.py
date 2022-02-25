"""Command line interface"""

import argparse
import sys


def main(args: argparse.Namespace) -> None:
    # TODO call actual method
    # decode_morse(args.WAVFILE)
    ...


def parse_args(args: list[str]) -> argparse.Namespace:
    """Parse arguments from command line"""
    parser = argparse.ArgumentParser(
        description="""Decode morse audio

        Read audio file in WAV format, extract the morse code and
        write translation into standard output."""
    )
    parser.add_argument("WAVFILE", help="Input audio file")
    return parser.parse_args(args)


if __name__ == "__main__":
    args = parse_args(sys.argv[1:])
    main(*args)

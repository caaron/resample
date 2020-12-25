import sys
import os
import ffmpeg
import argparse

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("-i","--input", help="file or directory to process")
    parser.add_argument("-s", "--sub", help="subtitles")
    parser.add_argument("-n", "--nop", help="no action, just print info and what would be done",
                        action="store_true")
    args = parser.parse_args()

    if not args.input:
        print("missing file. exiting...")
        exit(-1)
    if not args.sub:
        print("missing subs file. exiting...")
        exit(-1)

    input = ffmpeg.input(args.input)
    subs = ffmpeg.input(args.subs)
    (
        ffmpeg
        .filter([input, subs])
    )

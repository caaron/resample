import ffmpeg
import sys
import math
import os
import argparse


def resample(fname,tempname, params=None):
    try:
        stream = ffmpeg.input(fname)
        vcodec = params.get("video","h264")
        acodec = params.get("audio", "aac")
        vidbr =  params.get("vidbr", "2000k")
#        stream = ffmpeg.output(stream, tempname, vcodec=vcodec, crf=25, acodec=acodec, ar=48000, map="0")
        stream = ffmpeg.output(stream, tempname, vcodec=vcodec, **{'b:v':vidbr}, acodec=acodec)
        #ffmpeg.run(stream,capture_stdout=True)
        ffmpeg.run(stream)
        return True
    except Exception as ex:
        template = "An exception of type {0} occurred. Arguments:\n{1!r}"
        
        message = template.format(type(ex).__name__, ex.args)
        print(message)
        return False


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("-i","--input", help="file or directory to process")
    parser.add_argument("-v", "--verbosity", help="verbosity", action="count", default = 0 )
    parser.add_argument("-n", "--nop", help="no action, just print info and what would be done",
                        action="store_true")
    parser.add_argument("-r", "--bitrate", help="bitrate threshold (kbps) to resample", default=2000)
    parser.add_argument("-ac", "--audioCodec", help="audio codec", default="aac")
    args = parser.parse_args()

    if not args.input:
        print("missing file or directory name. exiting...")
        exit(-1)

    print(args.input)
    fname = args.input

    specs = ffmpeg.probe(fname)
    f = specs["format"]
    if args.verbosity > 0:
        print(specs)

    input = ffmpeg.input(fname)
    audio = input.audio

    rate = int(f["bit_rate"])
    if args.verbosity > 0:
        print("bitrate:{0}",rate)
    duration = float(specs["format"]["duration"])
    print("duration:" + duration)
    mins = float(duration)/60
    hrs = math.floor(mins/60)
    print("duration:%d:%d" % (hrs,mins))
    size = float(f["size"])
    print("filesize:"+size)

    desired_rate = 1805296
    tf = fname + ".new.mp4"
    if os.path.exists(tf):
        os.remove(tf)
    result = resample(fname,tf)
    if result is True:
        os.remove(fname)
        os.rename(tf,fname)
        print("Resampled " + fname)
    else:
        print("Resampling %s failed!" % fname)

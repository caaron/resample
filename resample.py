import ffmpeg
import sys
import math
import os


def resample(fname,tempname, params=None):
    try:
        stream = ffmpeg.input(fname)
        vcodec = params.get("video","h264")
        acodec = params.get("audio", "aac")
#        stream = ffmpeg.output(stream, tempname, vcodec=vcodec, crf=25, acodec=acodec, ar=48000, map="0")
        stream = ffmpeg.output(stream, tempname, vcodec=vcodec, crf=30, acodec=acodec)
        #ffmpeg.run(stream,capture_stdout=True)
        ffmpeg.run(stream)
        return True
    except Exception as ex:
        template = "An exception of type {0} occurred. Arguments:\n{1!r}"
        
        message = template.format(type(ex).__name__, ex.args)
        print(message)
        return False


if __name__ == '__main__':
    print(sys.argv[1])
    fname = sys.argv[1]

    specs = ffmpeg.probe(fname)
    f = specs["format"]
    print(specs)

    input = ffmpeg.input(fname)
    audio = input.audio

    rate = int(f["bit_rate"])
    print(rate)
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

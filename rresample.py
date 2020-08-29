import sys
import math
import os
import ffmpeg
import resample
import datetime
import argparse

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("-i","--input", help="file or directory to process")
    parser.add_argument("-v", "--verbosity", help="verbosity", action="count", default = 0 )
    parser.add_argument("-n", "--nop", help="no action, just print info and what would be done",
                        action="store_true")
    parser.add_argument("-k", "--keep", help="delete original files", action="store_true")
    parser.add_argument("-r", "--bitrate", help="bitrate threshold (kbps) to resample", default=2000)
    args = parser.parse_args()

    if not args.input:
        print("missing file or directory name. exiting...")
        exit(-1)
    print(sys.argv[1])
    max_br = args.bitrate * 1000
#    fname = args.input
    # if !isdir
    if os.path.isfile(args.input):
        print("process just one file")
        files_to_process = args.input
    # just do this one file
    # else assume the first arg is a dir and walk thru all the files recursively of that dir
    elif os.path.isdir(args.input):
        print("process directory recursively")
        files_to_process = {}
        cmds_to_process = []
        for (dirpath, dirnames, filenames) in os.walk(args.input):
            for filename in filenames:
                try:
                    pathfilename = os.sep.join([dirpath, filename])
                    specs = ffmpeg.probe(pathfilename)
                    fmt = specs["format"]
                    br = int(fmt["bit_rate"])
                    ac = 0
                    duration = 0;
                    for stream in specs["streams"]:
                        if stream["codec_type"] == "audio":
                            ac = int(stream["channels"])
                        if stream.get("duration",-1) == -1:
                            if False:
#                           if stream.get("tags",-1) is not -1:
                                tags = stream.get("tags")
                                s = [value for key, value in tags.items() if 'duration' in key.lower()]
                                ms = date.strptime(s)
                                duration = float(s[0])
                                print("found a duration of %f in tags" % duration)
                        else:
                            duration = stream["duration"]
                    #if (br > 66666666 or ac > 2) and ac > 0:
                    if float(duration) < 10:
                        if args.verbosity > 1:
    #                        print("skipping %s invalid duration" % (filename))
                            print("%s is not a valid video file" % os.sep.join([dirpath, filename]))
                    elif br < max_br:
                        print("skipping %s bitrate:%ik (%i MB)" % (filename, br / 1000, int(fmt["size"])/1000000))
                    else:
                        if args.nop:
                            print("resample %s bitrate:%ik (%i MB)" % (filename, br / 1000, int(fmt["size"])/1000000))
                        else:
                            files_to_process[pathfilename] = pathfilename

#                        print("%s is below bitrate threshold" % pathfilename)
                except KeyError:
                    if args.verbosity > 1:
                        print("%s is not a valid video file" % os.sep.join([dirpath, filename]))

                except Exception as ex:
                    template = "An exception of type {0} occurred. Arguments:\n{1!r}"
                    msg_type = template.format(type(ex).__name__, ex.args)
                    msg = str(ex.stderr).split(":")[-1]
                    print(msg)
                    if args.verbosity > 1:
                        if msg.rfind("Invalid") is not -1:
                            print("%s is not a valid video file" % os.sep.join([dirpath, filename]))
                        else:
                            print("%s causes unknown exception" % os.sep.join([dirpath, filename]))

    #print(files_to_process)
    for fname in files_to_process:
        tf = fname + ".new.mp4"
        if os.path.exists(tf) and not args.nop:
            os.remove(tf)
        specs = ffmpeg.probe(fname)
        fmt = specs["format"]
        br = int(fmt["bit_rate"])
        if args.nop:
            print("resample %s (%ikbps/%0.2fMbps)" % (fname,br/1000,br/(1000000)))
            result = False
        else:
            result = resample.resample(fname, tf)
        if result is True and args.keep is False:
            os.remove(fname)
            os.rename(tf,fname)
            print("Resampled " + fname)
        elif args.keep is False:
            pass
        else:
            print("Resampling %s failed!" % fname)




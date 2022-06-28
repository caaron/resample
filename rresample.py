import subprocess
import sys
import math
import os
import ffmpeg
import resample
import datetime
import argparse

#from plexapi.myplex import MyPlexAccount

import plexapi
#from plexapi import compat
#from plexapi.client import PlexClient
#from plexapi.server import PlexServer

SERVER_BASEURL = plexapi.CONFIG.get('auth.server_baseurl')
MYPLEX_USERNAME = plexapi.CONFIG.get('auth.myplex_username')
MYPLEX_PASSWORD = plexapi.CONFIG.get('auth.myplex_password')
CLIENT_BASEURL = plexapi.CONFIG.get('auth.client_baseurl')
CLIENT_TOKEN = plexapi.CONFIG.get('auth.client_token')


def tvshows(plex):
    return plex.library.section('TV Shows')

def movies(plex):
    return plex.library.section('Movies')

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("-i","--input", help="file or directory to process")
    parser.add_argument("-v", "--verbosity", help="verbosity", action="count", default = 0 )
    parser.add_argument("-n", "--nop", help="no action, just print info and what would be done",
                        action="store_true")
    parser.add_argument("-k", "--keep", help="delete original files", action="store_true")
    parser.add_argument("-m", "--mkv", help="convert mkv to mp4 even if just copy", action="store_true")
    parser.add_argument("-r", "--bitrate", help="bitrate threshold (kbps) to resample", default=2000)
    parser.add_argument("-w", "--watched", help="only resample if plex has marked as watched", action="store_true")
    args = parser.parse_args()

    if not args.input:
        parser.print_help(sys.stderr)
        exit(-1)
    print(sys.argv[1])
    max_br = int(args.bitrate) * 1000
    cmds_to_process = []
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
        for (dirpath, dirnames, filenames) in os.walk(args.input):
            for filename in filenames:
                audio_params = "copy"
                video_params = "copy"
                sub_params = "mov_text -metadata:s:s:0 language=eng"
                try:
                    # logic is: test each file if they have any of the following:
                    # video bitrate > 2000kbps or video codec is h265, convert to h264
                    # not aac, convert to aac
                    convert = False
                    pathfilename = os.sep.join([dirpath, filename])
                    specs = ffmpeg.probe(pathfilename)
                    fmt = specs["format"]
                    br = int(fmt["bit_rate"])
                    container = "mp4"
                    #resolution = specs["resolution"]

                    filesize = int(fmt["size"])/1000000
                    ac = 0
                    duration = 0
                    for stream in specs["streams"]:
                        if stream["codec_type"] == "audio":
                            ac = int(stream["channels"])
                            #if not aac, convert it to that
                            if stream["codec_name"] != "aac":
                                audio_params = "aac"
                                convert = True
                                if args.verbosity > 0:
                                    print("converting %s's audio to aac because its %s" % (filename, stream["codec_name"]))
                        if fmt["format_name"].find("matroska") != -1 and args.mkv is True:
                            pass    # convert mkv to mp4                            
                            convert = True
                            container = "mkv"
                            if args.verbosity > 0:
                                print("converting %s because its matroska" % (filename))

                        if stream.get("duration",-1) == -1:
                            pass
                            duration = 100      # REMOVE!!!!
                        else:
                            duration = stream["duration"]

                    if float(duration) < 10:
                        convert = False
                        if args.verbosity > 1:
    #                        print("skipping %s invalid duration" % (filename))
                            print("%s is not a valid video file" % os.sep.join([dirpath, filename]))
                    #elif br < max_br:
                    #    convert = False
                    #    print("skipping %s bitrate:%ik (%i MB)" % (filename, br / 1000, int(fmt["size"])/1000000))
                    #elif (br > max_br) and (filesize < 500):
                    #    print("skipping %s bitrate:%ik but filesize is only %i MB" % (filename, br / 1000, filesize))
                    elif (br > max_br):
                        convert = True
                        video_params = "h264"
                    else:
                        pass

                    if convert:
                        if args.nop:
                            if args.verbosity > 0:
                                #print("resample %s bitrate:%ik (%i MB)" % (filename, br / 1000, int(fmt["size"])/1000000))
                                print("resample %s (%ikbps/%0.2fMbps) using %s and %s" % (filename, br / 1000, br / (1000000), video_params, audio_params))
                        tempf = pathfilename + ".new.mp4"
                        cmdline = "%s %s %s" % (audio_params,video_params,sub_params)
                        params = {}
                        params["audio"]  = audio_params
                        params["video"] = video_params
                        params["subs"] = sub_params
                        params["vidbr"] = str(args.bitrate) + 'k'
                        stats ={}
                        stats["bitrate"] = br
                        stats["filesize"] = filesize
                        stats["format"] = fmt["format_name"]
                        stats["ac"] = ac
                        files_to_process[pathfilename] = pathfilename
                        cmd ={}
                        cmd["fname"] = pathfilename
                        #cmd["params"] = cmdline
                        cmd["params"] = params
                        cmd["stats"] = stats
                        cmd["tmpfname"] = tempf
                        cmd["container"] = container
                        if container == "mkv":
                            cmd["newfname"] = os.path.splitext(pathfilename)[0] + ".mp4"
                        cmds_to_process.append(cmd)

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
                        if msg.rfind("Invalid") != -1:
                            print("%s is not a valid video file" % os.sep.join([dirpath, filename]))
                        else:
                            print("%s causes unknown exception" % os.sep.join([dirpath, filename]))

    #print(files_to_process)
    print("Files to be processed:")
    for cmd in cmds_to_process:
        fname = cmd["fname"]
        tf = fname + ".new.mp4"
        if os.path.exists(tf) and not args.nop:
            os.remove(tf)
        #specs = ffmpeg.probe(fname)
        fmt = cmd["stats"]["format"]
        #br = int(fmt["bit_rate"])
        br = cmd["stats"]["bitrate"]
        stats = cmd["stats"]
        params = cmd["params"]
        print("resample %s (%ikbps/%0.2fMbps), size %iMB using %s and %s" % (fname, br / 1000, br / (1000000), stats["filesize"], params["video"], params["audio"] ))
        if args.nop:
            result = False
        else:
            result = resample.resample(fname, tf, params=params)
#            subp = subprocess.Popen(['ffmpeg','-i','fname',params,tf],stdout=subprocess.PIPE,stderr=subprocess.STDOUT)
#            stdout,stderr = subp.communicate()
        if result is True and args.keep is False:
            os.remove(fname)
            if cmd["container"] == "mkv":
                os.rename(tf,cmd["newfname"])
            else:
                os.rename(tf,fname)

            print("Resampled " + fname)
        elif args.keep is False:
            pass
        else:
            print("Resampling %s failed!" % fname)




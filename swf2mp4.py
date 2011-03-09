#!/usr/bin/env python

# swf2vid copyright  2011 Justin Boisvert, Zac Sturgeon, Alec Gorge
# Requires gfx.pyd, Python 2.6.*, gnash, ffmpeg (tested against gnash 0.8.[8-9dev] and ffmpeg SVN-r23418)
# First version EVAH.
# Monday, March 07 2011

import os
import shutil
import sys
import gfx
import subprocess

if len(sys.argv) != 3:
	print "Usage:  "+sys.argv[0]+" input.swf output.mp4"
	exit()
	
inp = os.path.abspath(sys.argv[1])

audio_file = os.path.join(os.path.dirname(inp), os.path.basename(inp) + ".TMP.wav")
frame_dir = os.path.join(os.path.dirname(inp), "output-{0}/".format(os.path.basename(inp)))
frame_format = frame_dir + "gnash-%d.png"

out = sys.argv[2]
swf = gfx.open("swf", inp)

print "Processing {0}".format(inp)

length = int(raw_input("Enter video length (seconds): "))
frames = swf.pages # the number of frames

print "FPS: {0}".format(frames/length)
print "Frames to write: "+str(frames)

print "Extracting audio..."
audio_result = subprocess.Popen(['gnash', '--once', '-A', audio_file, '-r', '2', inp], shell=True)
audio_result.wait()
if audio_result.returncode != 0:
	print "Something went wrong! "+str(ret)
	exit()

print "Writing out frames..."
scrn_result = subprocess.Popen(['gnash', '--once', '--screenshot', str(range(1,frames))[1:].rstrip(']').replace(' ',''), '--screenshot-file', frame_format, inp], shell=True)
scrn_result.wait()
if scrn_result.returncode != 0:
	print "gnash exited non-zero. Something may have gone wrong"
	exit()
	
print "Finished writing frames."
print "Rendering video..."

#FFMPEG command:
#TODO Add ffmpeg options to this cli.

ffmpeg = subprocess.Popen(['ffmpeg', '-i', audio_file, '-sameq', '-f', 'image2', '-i', frame_format, out], shell=True)
ffmpeg.wait()
if ffmpeg.returncode != 0:
	print "ffmpeg error: " + str(ret)
	exit()
	
print "Rendering complete. Cleaining up..."
os.remove(audio_file)
shutil.rmtree(frame_dir)
exit()

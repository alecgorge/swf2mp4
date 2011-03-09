#!/usr/bin/env python

# swf2vid copyright  2011 Justin Boisvert, Zac Sturgeon, Alec Gorge
# Requires gnash, ffmpeg (tested against gnash 0.8.8 and ffmpeg 
# First version EVAH.
# Monday, March 07 2011

import os
import sys

if len(sys.argv) != 3:
	print "Usage:  "+sys.argv[0]+" input.swf output.mpeg"
	exit()
	
inp = sys.argv[1]
out = sys.argv[2]

length = int(raw_input("Enter video length (seconds): "))
print "Warn: defaulting to 25 fps."
frames = int(length)*25
print "Frames to write: "+str(frames)


print "Extracting audio..."
ret = os.system("gnash --once -A /tmp/gnash.wav -r 2 "+inp)
if ret != 0:
	print "Something went wrong! "+str(ret)
	exit()

print "Writing out frames..."
ret = os.system("gnash --once --screenshot "+str(range(1,frames))[1:].rstrip(']').replace(' ','')+ " --screenshot-file /tmp/gnash-%f.png "+inp)

if ret != 0:
	print "gnash exited non-zero. Something may have gone wrong"
	exit()
	
print "Finished writing frames."
print "Rendering video..."

#FFMPEG command:
#TODO Add ffmpeg options to this cli.

ret = os.system("ffmpeg -i /tmp/gnash.wav -sameq -f image2 -i /tmp/gnash-%d.png "+out)
if ret != 0:
	print "ffmpeg error."
	exit()
	
print "Rendering complete. Cleaining up..."
os.system("rm -rf /tmp/gnash*")
exit()

#!/usr/bin/env python
#-*- coding:utf-8 -*-

# swf2vid for linux. Copyright © 2011 Justin Boisvert, Zac Sturgeon, Alec Gorge
# Requires swftool, Python 2.6.*, gnash, ffmpeg (tested against gnash 0.8.[8-9dev] and ffmpeg SVN-r23418)

# Last modified by Zac on Wednesday, March 09 2011
# Have a bit of cleaning up to do.
# Can only run one instance at a time right now because I'm a little lazy with the paths.
# Frames should be written to /tmp for best performance.  Not everyone's /home is big enough
# on some systems.  Alec's Shell forks don't pass the correct arguments for some reason.
# I changed them back to os.system() because shell exploits aren't very useful on a local desktop.
# We'll need to change this if we write a CGI version, but for now this works.

import os
import shutil
import sys
import subprocess
import commands

frame_dir = "/tmp/"
tmpdir = "/tmp"

#for debug
writeAudio = True
writeFrames = True
writeMpeg = True
	
def check_deps():
	platform = commands.getoutput("lsb_release -sa | head -1") #SHELL FORK. (CGI!)
	
	#check for swftools
	swfdump = commands.getstatusoutput('which swfdump')
	if swfdump[0] != 0:
		print "Err: swfdump is not installed!"
		if platform == "Ubuntu" or platform == "Debian":
			inst = raw_input("Would you like to install it? [y/n]: ")
			if inst.upper() == "Y":
				apt = commands.getstatusoutput('sudo apt-get install swftools')
				swfdump = commands.getstatusoutput('which swfdump')
				if apt != 0 or swfdump[0] != 0:
					print "Error in install. Exiting."
					exit()
		if platform == "Fedora":
			print "You're on your own for now. I'll make an RPM later."
			exit()
		
	#check for gnash
	gnash = commands.getstatusoutput('which gnash')
	if gnash[0] != 0:
		print "Err:  gnash is not installed!"
		if platform == "Ubuntu" or platform == "Debian":
			inst = raw_input("Would you like to install it? [y/n]: ")
			if inst.upper() == "Y":
				apt = commands.getstatusoutput('sudo apt-get install gnash')
				gnash = commands.getstatusoutput('which gnash')
				if apt != 0 or gnash[0] != 0:
					print "Error in install. Exiting."
					exit()
		if platform == "Fedora":
			inst = raw_input("Would you like to install it? [y/n]: ")
			if inst.upper() == "Y":
				apt = commands.getstatusoutput("su -c 'yum install gnash'")
				gnash = commands.getstatusoutput('which gnash')
				if apt != 0 or gnash[0] != 0:
					print "Error in install. Exiting."
					exit()
					
	#check for ffmpeg
	ffmpeg = commands.getstatusoutput('which ffmpeg')
	if ffmpeg[0] != 0:
		print "Err: ffmpeg is not installed!"
		if platform == "Ubuntu" or platform == "Debian":
			inst = raw_input("Would you like to install it? [y/n]: ")
			if inst.upper() == "Y":
				apt = commands.getstatusoutput('sudo apt-get install ffmpeg')
				ffmpeg = commands.getstatusoutput('which ffmpeg')
				if apt != 0 or ffmpeg[0] != 0:
					print "Error in install. Exiting."
					exit()
		if platform == "Fedora":
			inst = raw_input("Would you like to install it? [y/n]: ")
			if inst.upper() == "Y":
				apt = commands.getstatusoutput("su -c 'yum install ffmpeg'")
				ffmpeg = commands.getstatusoutput('which ffmpeg')
				if apt != 0 or ffmpeg[0] != 0:
					print "Error in install. Exiting."
					exit()
	
	if swfdump[0] != 0 or gnash[0] != 0 or ffmpeg[0] != 0:
		return 1
	else:
		return 0
		
if check_deps(): #check for things we need
	print "Missing deps. Exiting. "
	exit()
	
if len(sys.argv) != 3:
	print "Usage:  "+sys.argv[0]+" input.swf output.mp4"
	exit()

inp = os.path.abspath(sys.argv[1])

#ffmpeg doesn't like the frame_format path.  Exits with I/O error.
#the screenshots never show up, driectory is never created.
audio_file = os.path.join(os.path.dirname(inp), os.path.basename(inp) + ".TMP.wav")
#frame_dir = os.path.join(os.path.dirname(inp), "output/".format(os.path.basename(inp)))
frame_format = tmpdir + "/gnash-%f.png"

out = sys.argv[2]
#get frames
swfdump = commands.getstatusoutput('swfdump -f '+inp)
if swfdump[0] != 0:
	print "Err: swfdump exited non-zero."
	exit()
frames = int(swfdump[1].split(' ')[1])
print "Debug: Frames - "+str(frames)

#get framerate
swfdump = commands.getstatusoutput('swfdump -r '+inp)
if swfdump[0] != 0:
	print "Err: swfdump exited non-zero."
	exit()

rate = float(swfdump[1].split(' ')[1])
print "Debug: Rate - "+str(rate)

print "Processing {0}".format(inp)

print "Length (seconds): ".format(frames/rate)
print "Frames to write: "+str(frames)

#Although this is the /right/ way to do it, it doesn't give gnash the right arguments for 
#some reason.  We don't really need forking (except maybe if we wrote this for CGI)
#I know it's good practice, but I don't think that a desktop app such as this really needs
#to care about protecting against shell exploits.  Just don't run as root.
#audio_result = subprocess.Popen(['gnash', '--once', '-A', audio_file, '-r', '2', inp], shell=True)
#audio_result.wait()
if writeAudio:
	print "Extracting audio... ("+inp+")"
	audio_result = os.system('gnash --once -A '+audio_file+' -r 2 '+inp)

	if audio_result != 0:
		print "Something went wrong! "+str(audio_result)
		exit()

if writeFrames:
	print "Writing out frames... ("+frame_format+")"
	#scrn_result = subprocess.Popen(['gnash', '--once', '--screenshot', str(range(1,frames))[1:].rstrip(']').replace(' ',''), '--screenshot-file', frame_format, inp], shell=True)
	#scrn_result.wait()
	scrn_result = os.system('gnash --once --screenshot '+str(range(1,frames))[1:].rstrip(']').replace(' ','')+' --screenshot-file '+frame_format+' '+inp)
	if scrn_result != 0:
		print "gnash exited non-zero. Something may have gone wrong"
		exit()

	print "Finished writing frames."
print "Rendering video..."

#FFMPEG command:
#TODO Add ffmpeg options to this cli.

#ffmpeg = subprocess.Popen(['ffmpeg', '-i', audio_file, '-sameq', '-f', 'image2', '-i', frame_format, out], shell=True)
#ffmpeg.wait()
ffmpeg = os.system('ffmpeg -i '+audio_file+' -sameq -f image2 -i '+tmpdir+'/gnash-%d.png '+out)
if ffmpeg != 0:
	print "ffmpeg error: " + str(ffmpeg)
	exit()

print "Rendering complete. Cleaining up..."
os.remove(audio_file)
os.system('rm -rf /tmp/gnash*')
exit()

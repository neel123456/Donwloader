from downloaderOOP import *
import sys,os,time
def lookupArg(name):
	try:
		place = sys.argv.index("-"+name)
	except:
		return -1
	return sys.argv[place + 1]


url = sys.argv[1]
down = downloadUrl(url)
name = lookupArg("name")
if name != -1:
	down.title = name
down.bbdownload();


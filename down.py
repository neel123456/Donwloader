from ytlist import *
import sys,os,time
def lookupArg(name):
	try:
		place = sys.argv.index("-"+name)
	except:
		return -1
	return sys.argv[place + 1]


arg1 = sys.argv[1]
if arg1 == "--file":
	f = open(sys.argv[2])
	urls = f.read().split('\n')
	urls = list(set(urls))
	print(len(urls))
	cnt = 0
	for url in urls:
		if url=='':
			continue
		if "youtube" in url:
			vid = ytvideo(url)
			vid.download()
		else:
			down = downloadUrl(url)
			down.bbdownload()
		cnt += 1
		print(cnt)
else:
	down = downloadUrl(arg1)
	down.bbdownload()


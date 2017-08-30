from downloaderOOP import *
import sys,os,time
try:
    url=sys.argv[1]
    down=downloadUrl(url)
    down.bbdownload()
except:
    print("Failed download for "+sys.argv[1])

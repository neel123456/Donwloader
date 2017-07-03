import urllib.request as ur
from bs4 import BeautifulSoup
from ytvid import *
class ytlist(object):
    def __init__(self,url):
        self.url=url
        self.videos=[]
        resp=ur.urlopen(url)
        #print(resp.status)
        if resp.status==200:
            print("OK 200")
            page=resp.read()
        else:
            print("FOUND %d" % (resp.status))
            ## for now
            exit(1)
        #####       Getting List of Videos      #####
        soup=BeautifulSoup(page,"html.parser")
        ##print(soup.prettify())
        #print(len(soup.find_all('a',class_="pl-video-title-link")))
        anchors=soup.find_all('a',class_="pl-video-title-link")
        for i in anchors:
            self.videos.append("https://youtube.com"+i['href'])
        #print(self.videos)

    def downloadPlaylist(self):
        for i in range(len(self.videos)):
            print("ytlist:: Downloading %d of %d " % (i+1,len(self.videos)))
            current=ytvideo(self.videos[i])
            current.download()
            print("ytlist:: Completed downloading %d" %(i+1))

    

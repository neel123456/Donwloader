import pafy
from downloaderOOP import *
class ytvideo(object):
    def __init__(self,url):
        self.baseurl=url
        self.streamNumber=None   ## None will default to best available ##
        try:
            self.obj=pafy.new(self.baseurl)
        except:
            print("Error getting downloadable urls.Check your url and internet connection")
            exit(1)
        self.title=self.obj.title+"."+self.obj.getbest().extension
        print(self.title)
        
    def __str__(self):
        print(self.obj)

    def printStreams(self):
        for i in range(len(self.obj.allstreams)):
            print("%d "%(i)+str(self.obj.allstreams[i]))

    def setStream(self,streamNumber):
        self.streamNumber=streamNumber

    def download(self):
        if self.streamNumber:
            downurl=self.obj.allstreams[self.streamNumber].url
        else:
            downurl=self.obj.getbest().url
        download=downloadUrl(downurl,self.obj.title)
        download.sendHead()
        download.setDefaultFraglist()
        download.downloadAllFrags()
  

### Import Libraries ###
import requests
import urllib.request as ur
import sys,os,threading,time
from bs4 import BeautifulSoup as bs
### Import Files ###
import utils

class downloadUrl(object):
    def __init__(self,url,title=None):
        self.url=url
        self.byteAllow=None
        self.headers=None
        self.frags=64
        self.title=utils.removeSlash(title)
        self.length=None
        self.done=False
        self.percent=None
        self.fraglist=None
        self.fragsize=[-1 for i in range(self.frags)]
        self.donesize=[0 for i in range(self.frags)]
        self.skipmerge=False
        self.running=True
        self.chunk=16*1024
        self.wait=15
        if not self.title:
            self.title=url.split('/')[-1]
            print("title set to "+self.title)
        if "youtube" in self.url or "youtu.be" in self.url:
            self.isTube=True
        else:
            self.isTube=False
        

    def setFrags(self,frags):
        if frags<2 or frags>32:
            print("WARNING: fragments must be between 2 to 32 defaulting to 5")    
        self.frags=frags
        
    def __str__(self):
        return str("url: "+self.url)

    def sendHead(self):
        print("sending Head request")
        response=requests.head(self.url)
        if response.status_code==200 and 'Content-Length' in response.headers:
            print("OK 200")
            self.headers=response.headers
            self.length=int(self.headers['Content-Length'])
            print("length: "+str(self.length))
            assert self.length>0,"Something went wrong"

            if self.headers['Accept-Ranges']=='bytes':
                self.byteAllow=True
            else:
                self.byteAllow=False
        elif response.status_code>300 and response.status_code<309:
            print(str(response.status_code)+" "+response.reason)
            print("Trying to follow redirection to %s"%(response.headers['Location']))
            self.url=response.headers['Location']
            self.sendHead()
        else:
            print(str(response.status_code)+"received"+response.reason)
            self.byteAllow=False
            self.headers=response.headers
            self.length=False
            
    def downloadOld(self):
        chunk=16*1024    ### Chunk size = 1 kilobyte ###
        ###  Prepare request
        sendheaders={'User-Agent':'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/35.0.1916.47 Safari/537.36'}
        reqst=ur.Request(self.url,headers=sendheaders)
        data=ur.urlopen(reqst)
        fp=open(self.title,"wb")
        percentThread=threading.Thread(target=utils.checkSize,args=(self.title,self.length))
        percentThread.start()
        while True:
            cnk=data.read(chunk)
            if not cnk: 
                break
            fp.write(cnk)
        fp.close()
        self.done=True
        percentThread.join()
        print()
        print("done!")

    def downloadFrag(self,start,end,num):
        oldstart=start
        fname=self.title+".frag"+str(num)
        self.fragsize[num]=end-start+1
        if os.access(fname,os.F_OK):
            start+=os.stat(fname).st_size
            self.donesize[num]=os.stat(fname).st_size
            assert start-1<=end,"Looks like a problem to me start is greater than or equal to end. \
Cannot resume! start=%d end=%d num=%d" %(start,end,num)
            if start==end+1:
                return;
            #print("Download for %d fragment will resume from %d" % (num,start),end='\r')
        print("starting download for %d frag " % num,end='\r')
        sendheaders={'Range':'bytes=%d-%d'%(start,end),'User-Agent':'Mozilla/5.0 \
(Macintosh; Intel Mac OS X 10_9_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/35.0.1916.47 Safari/537.36'}
        connection=ur.Request(self.url,None,sendheaders)
        try:
            down=ur.urlopen(connection,timeout=20)
        except:
            self.skipmerge=True;
            print("Error occured frag=%d"%num)
            return;
        fp=open(self.title+".frag"+str(num),"ab")
        writer=threading.Thread(target=self.writeChunks,args=(fp,down,num))
        writer.start()
        count=0
        while True:
            downloaded=self.donesize[num]
            if writer.is_alive():
                time.sleep(1)
                count+=1                ## wait for something to change
                if count%self.wait==0 and self.donesize[num]==downloaded:
                    print("Closing file for non responsive fragment %d" % (num),end='\r')
                    fp.close()      ## Not responding actions..
                    ########    Testing...      ####### Segmentation Fault prone!
                    print("Restarting same frag",end='\r')
                    self.downloadFrag(oldstart,end,num)
                    return -1;
            else:
                break
        #print("finished download for frag %d\n" % (num))

    def writeChunks(self,f,connection,num):
        try:
            while(True):
                cnk=connection.read(self.chunk)
                if not cnk:
                    break
                f.write(cnk)
                self.donesize[num]+=len(cnk)
        except:
            print("Exiting from not responding connection",end='\r')
            return -1;  
        
##    def downloadFragUC(self,start,end,num):
##        try:
##            assert end-start < 1024*1024*2,"Don't use unchunked for big frags... Wanna crash your pc?"
##            fname=self.title+".frag"+str(num)
##            self.fragsize[num]=end-start+1
##            if os.access(fname,os.F_OK):
##                start+=os.stat(fname).st_size
##                self.donesize[num]=os.stat(fname).st_size
##                assert start-1<=end,"Looks like a problem to me start is greater than or equal to end. Cannot resume!"
##                if start==end+1:
##                    return;
##                #print("Download for %d fragment will resume from %d" % (num,start))
##            sendheaders={'Range':'bytes=%d-%d'%(start,end),'User-Agent':'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/35.0.1916.47 Safari/537.36'}
##            connection=ur.Request(self.url,None,sendheaders)
##    ##        connection.headers['Range']="bytes=%d-%d" % (start,end)
##            
##    ##        print("starting download for frag %d\n" % (num))
##            down=ur.urlopen(connection)
##            ##chunk=32*1024
##            fp=open(self.title+".frag"+str(num),"ab")
##            ##while(True):
##            data=down.read();
##            fp.write(data)
##            self.donesize[num]+=len(data)
##            fp.close()
##            #print("finished download for frag %d\n" % (num))
##        except:
##            self.downloadFragUC(start,end,num)
        
    def setDefaultFraglist(self):
        assert (int(self.length>0)),"Your download file kinda sucks"
        self.fraglist=[]
        self.fraglist.append((0,int((self.length-1)*(float(1)/self.frags))));
        for i in range(1,self.frags):
            self.fraglist.append((self.fraglist[-1][1]+1,int((self.length-1)*(float(i+1)/self.frags))))    
        ##print("Debug: "+str(self.fraglist))
        
##    def downloadAllFrags(self):
##        if self.length==None:
##            self.sendHead()
##            self.setDefaultFraglist()
##        if self.length==False or self.byteAllow==False:
##            print("Can not download by fragments.")
##            print("Falling back to old download style.")
##            self.downloadOld()
##            return;
##        else:
##            self.setDefaultFraglist()
##            if os.access(self.title,os.F_OK) and os.stat(self.title).st_size==self.length:
##                print("looks like file is downloaded already")
##                return;
##            print("downloading "+'%.2f'%(self.length/(1024*1024.0))+" MB");
##            threadlist=[]
##            for i in range(self.frags):
##                t=threading.Thread(target=self.downloadFrag,kwargs={'start':self.fraglist[i][0],'end':self.fraglist[i][1],'num':i}) 
##                t.start()
##                threadlist.append(t)
##            time.sleep(1)
##            progress=threading.Thread(target=self.generateProgressBar)
##            progress.start()
##            threadlist.append(progress)
##            for t in threadlist:
##                t.join()
##            print()
##            print("done downloading")
##            print("Starting to merge %d files"%(self.frags))
##            utils.catAll(self.title,self.frags)
##            print()
            
    def setbbfraglist(self):
        if self.length==None:
            self.sendHead()
        #assert self.length>128*1024*1024,"Don't use bandwidth buster for small files!!"
        self.fraglist=[]
        MB=1024*1024
        first=0
        last=MB-1
        cnt=0
        while first<=self.length-1:
            if last>self.length-1:
                last=self.length-1
            self.fraglist.append((first,last))
            first=last+1
            last=first+MB-1
            cnt+=1
        self.frags=cnt
        self.fragsize=[-1 for i in range(self.frags)]
        self.donesize=[0 for i in range(self.frags)]
        #print(self.fraglist)
        print(self.frags)

    def setconstantfrags(self,kbs):
        if self.length==None:
            self.sendHead()
        #assert self.length>128*1024*1024,"Don't use bandwidth buster for small files!!"
        self.fraglist=[]
        size=1024*kbs
        first=0
        last=size-1
        cnt=0
        while first<=self.length-1:
            if last>self.length-1:
                last=self.length-1
            self.fraglist.append((first,last))
            first=last+1
            last=first+size-1
            cnt+=1
        self.frags=cnt
        self.fragsize=[-1 for i in range(self.frags)]
        self.donesize=[0 for i in range(self.frags)]
        #print(self.fraglist)
        print(self.frags)
        
    def bbdownload(self,frags=64):
        if self.length==False or self.byteAllow==False:
            print("Can not download by fragments.")
            print("Falling back to old download style.")
            self.downloadOld()
            return;
        else:
            self.sendHead()
            if os.access(self.title,os.F_OK) and os.stat(self.title).st_size==self.length:
                print("looks like file is downloaded already")
                return;
            print("downloading "+'%.2f'%(self.length/(1024*1024.0))+" MB");
            
            if self.length/(1024*1024.0) < 2:
                self.setconstantfrags(64)
                self.chunk=1*1024                   #64 KB fragments
            elif self.length/(1024*1024.0) < 16:
                self.setconstantfrags(64)          #128KB fragments
                self.chunk=2*1024
            elif self.length/(1024*1024.0) < 32:
                self.setconstantfrags(128)
                self.chunk=2*1024
            elif self.length/(1024*1024.0) < 1024:
                self.setconstantfrags(1024)
                self.chunk=8*1024
            else:
                self.setconstantfrags(10*1024)
                self.chunk=16*1024
                self.wait=20
            threadlist=[]
            #print(threading.active_count())
            nextFrag=0
            progress=threading.Thread(target=self.generateProgressBar)
            progress.start()
            #threadlist.append(progress)
            while True:                             ## Change here...Bug: active count may be more than actual, The orphened connections.. 
                ## count live count each time..
                if threading.active_count()<1+frags:
                    t=threading.Thread(target=self.downloadFrag,kwargs={'start':self.fraglist[nextFrag][0],'end':self.fraglist[nextFrag][1],'num':nextFrag})
                    t.start()
                    threadlist.append(t)
                    nextFrag+=1
                    time.sleep(0.001)               ## Server should not feel that she's under attack..
                    if nextFrag==self.frags:
                        break
            for i in threadlist:
                i.join()
            print()
            print("done downloading")
            if self.skipmerge:
                print("Can't merge...still have to download the DEAD")
                self.running=False
                return;
            print("Starting to merge %d files"%(self.frags))
            self.running=False
            utils.catAll(self.title,self.frags)
            print()

    def generateProgressBar(self):
        sleepTime=2         ### in seconds(Using variable to manage speeds ###
        prevDoneSize=0
        while True:
            #print(str(self.donesize)+str(self.fragsize))
            if not self.running:
                break;
            curDoneSize=sum(self.donesize)
            utils.printProgressBar(curDoneSize*100.0/self.length,speed=(curDoneSize-prevDoneSize)/sleepTime/1024)
            if self.donesize==self.fragsize:
                break
            time.sleep(sleepTime)
            prevDoneSize=curDoneSize


        

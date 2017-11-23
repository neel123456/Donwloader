### Import Libraries ###
import requests
import urllib.request as ur
import sys,os,threading,time
from bs4 import BeautifulSoup as bs
import socket
import subprocess
### Import Files ###
import utils

class downloadObject(object):
    def __init__(self, urls, interfaces, title = None):
        self.urls=urls
        self.ips=[]
        self.interfaces = interfaces;
        self.byteAllow=True
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
        self.wait=10
        self.tries=3
        if not self.title:
            self.title=urls[0].split('/')[-1]
            if '?' in self.title:
                self.title = self.title.split('?')[0]
            print("title set to "+self.title)

    def sendHead(self):
        length = self.verifyUrls()
        print(length)
        
    def verifyUrls(self):
        sendheaders={'User-Agent':'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/35.0.1916.47 Safari/537.36'}
        for url in self.urls:
            response=requests.head(url)
            if response.status_code==200 and 'Content-Length' in response.headers:
                headers=response.headers
                if not "length" in locals():
                    length=int(headers['Content-Length'])
                else:
                    length_new = int(headers['Content-Length'])
                    if length_new != length:
                        print("Length mismatch")
                        return False;
        return length

    def getIPs(self):
        for url in self.urls:
            hostname = url.split('/')[2]
            print(hostname)
            ip = socket.gethostbyname(hostname)
            if not ip in self.ips: self.ips.append(ip)

    def getDefaultGateway(self,interface):
        answer = subprocess.check_output("/usr/bin/ip","route",shell=True)
        print(answer)
        for line in answer.split("\n"):
            words = line.split()
            if "dev" in words and "via" in words and interface in words:
                return words[2]
        
    def modifyRoutingTable(self):
        assert len(self.ips) == len(self.interfaces)
        for i in range(len(self.ips)):
            os.system("route add -host %s dev %s" % (self.ips[i], self.interfaces[i]))
        

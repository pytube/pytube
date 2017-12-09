import urllib2
from bs4 import BeautifulSoup as bs
from pytube import YouTube
import re


def playlist(url):
    req = urllib2.urlopen(url)

    res=req.read()

    soup=bs(res,'html.parser')

    list = soup.find_all('a',{'class':'pl-video-title-link'})
    files_in_pl = []
    for link in list:
        files_in_pl.append('https://www.youtube.com'+link.get('href').split('&')[0])
        
    for link in files_in_pl:
        print 'downloading '+YouTube(link).title
        YouTube(link).streams.first().download()
        
if __name__ == '__main__':
    inurl = raw_input()
    print inurl
    ret = re.search('com(.+?)\?',inurl)
    if(ret != None):
        ret = ret.group(1)
    else:
        print 'wrong url'
        quit()
    if(ret != '/playlist'):
        print 'no url'
        quit()
    playlist(inurl)
    

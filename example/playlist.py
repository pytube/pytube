"""script to download all videos in a playlist"""

import urllib2
from bs4 import BeautifulSoup as bs
from pytube import YouTube
import re


def playlist(url):
    req = urllib2.urlopen(url)
    res = req.read()
    soup = bs(res, 'html.parser')
    list = soup.find_all('a', {'class': 'pl-video-title-link'})
    files_in_pl = []
    for link in list:
        vid_id = link.get('href').split('&')[0]
        files_in_pl.append('https://www.youtube.com' + vid_id)

    for link in files_in_pl:
        YouTube(link).streams.first().download()


if __name__ == '__main__':
    inurl = raw_input('Enter playlist url : ')
    ret = re.search('com(.+?)\?', inurl)
    if(ret is not None):
        ret = ret.group(1)
    else:
        quit()
    if(ret != '/playlist'):
        quit()
    playlist(inurl)

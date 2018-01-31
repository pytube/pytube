# -*- coding: utf-8 -*-
"""
Module to download a complete playlist from a youtube channel
"""
from __future__ import print_function
import requests
from bs4 import BeautifulSoup as bs
from pytube.__main__ import YouTube


class Playlist(object):
    """
    Handles all the task of manipulating and downloading
    a whole YouTube playlist
    """

    def __init__(self, url):
        self.playlist_url = url
        self.video_urls = []

    def construct_playlist_url(self):
        """
        There are two kinds of playlist urls in YouTube. One that
        contains watch?v= in URL, another one contains the "playlist?list="
        portion. It is preferable to work with the later one.
        :return: playlist url -> string
        """

        if "watch?v=" in self.playlist_url:
            base_url = "https://www.youtube.com/playlist?list="
            playlist_code = self.playlist_url.split("&list=")[1]
            return base_url + playlist_code

        # url is already in the desired format, so just return it
        return self.playlist_url

    def populate_video_urls(self):
        """
        Get the links of all the videos in playlist and populate video_urls
        list
        :return: urls -> string
        """

        base_url = "https://www.youtube.com"
        url = self.construct_playlist_url()
        req = requests.get(url)

        soup = bs(req.text, "html.parser")
        link_list = soup.find_all(attrs={"class": "pl-video-title-link"})

        for link in link_list:
            video_id = link.get("href").split("&")[0]
            complete_url = base_url + video_id
            # print complete_url
            self.video_urls.append(complete_url)

    def download_all(self):
        """
        Download all the videos in the the playlist. Initially, download
        resolution is 720p (or highest available), later more option
        should be added to download resolution of choice
        TODO: Add option to download resolution of user's choice
        :return: None
        """

        self.populate_video_urls()
        print("Total videos found:", len(self.video_urls))
        # print(self.video_urls)
        print("Starting download...\n")

        for link in self.video_urls:
            yt = YouTube(link)

            # the try/except is done to prevent the odd UnicodeEncodeError
            try:
                print("Downloading:", yt.title)
            except UnicodeEncodeError:
                print("(title cannot be shown due to unicode error)")

            yt.streams.filter(progressive=True,
                              subtype="mp4").order_by(
                "resolution").desc().first().download()

        print("Download complete")

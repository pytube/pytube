# -*- coding: utf-8 -*-
"""
Module to download a complete playlist from a youtube channel
"""
import logging

from pytube import request
from pytube.__main__ import YouTube

logger = logging.getLogger(__name__)


class Playlist(object):
    """Handles all the task of manipulating and downloading a whole YouTube
    playlist
    """

    def __init__(self, url):
        self.playlist_url = url
        self.video_urls = []

    def construct_playlist_url(self):
        """There are two kinds of playlist urls in YouTube. One that
        contains watch?v= in URL, another one contains the "playlist?list="
        portion. It is preferable to work with the later one.

        :return: playlist url -> string
        """

        if 'watch?v=' in self.playlist_url:
            base_url = 'https://www.youtube.com/playlist?list='
            playlist_code = self.playlist_url.split('&list=')[1]
            return base_url + playlist_code

        # url is already in the desired format, so just return it
        return self.playlist_url

    def parse_links(self):
        """Parse the video links from the page source, extracts and
        returns the /watch?v= part from video link href
        It's an alternative for BeautifulSoup

        :return: list
        """

        url = self.construct_playlist_url()
        req = request.get(url)

        # split the page source by line and process each line
        content = [x for x in req.split('\n') if 'pl-video-title-link' in x]
        link_list = [x.split('href="', 1)[1].split('&', 1)[0] for x in content]

        return link_list

    def populate_video_urls(self):
        """Construct complete links of all the videos in playlist and
        populate video_urls list

        :return: urls -> string
        """

        base_url = 'https://www.youtube.com'
        link_list = self.parse_links()

        for video_id in link_list:
            complete_url = base_url + video_id
            self.video_urls.append(complete_url)

    def download_all(self, download_path=None, file_number_prefix=True):
        """Download all the videos in the the playlist. Initially, download
        resolution is 720p (or highest available), later more option
        should be added to download resolution of choice

        TODO(nficano): Add option to download resolution of user's choice
        """

        def path_num_prefix_generator():
            """
            This generator function generates number prefixes for the items in the playlist.
            If you have a playlist of 100 videos it will number them like this:
            001, 002, 003 ect, up to 100.
            It also adds a space after the number.
            :return: prefix: string
            """
            digits = len(str(len(self.video_urls)))
            i = 1
            while True:
                prefix = str(i)
                if len(prefix) < digits:
                    for f in range(digits - len(prefix)):
                        prefix = "0" + prefix
                prefix += " "
                i += 1
                yield prefix

        self.populate_video_urls()
        logger.debug('total videos found: ', len(self.video_urls))
        logger.debug('starting download')

        prefix_gen = path_num_prefix_generator()

        for link in self.video_urls:
            yt = YouTube(link)

            # TODO: this should not be hardcoded to a single user's preference
            dl_stream = yt.streams.filter(
                progressive=True, subtype='mp4',
            ).order_by('resolution').desc().first()

            logger.debug('download path: %s', download_path)
            if file_number_prefix:
                prefix = next(prefix_gen)
                logger.debug('file prefix is: %s', prefix)
                dl_stream.download(download_path, filename_prefix=prefix)
            else:
                dl_stream.download(download_path)
            logger.debug('download complete')

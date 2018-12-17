# -*- coding: utf-8 -*-
"""
Module to download a complete playlist from a youtube channel
"""
import json
import logging
import re
from collections import OrderedDict

from pytube import request
from pytube.__main__ import YouTube

logger = logging.getLogger(__name__)


class Playlist(object):
    """Handles all the task of manipulating and downloading a whole YouTube
    playlist
    """

    def __init__(self, url, suppress_exception=False):
        self.playlist_url = url
        self.video_urls = []
        self.suppress_exception = suppress_exception

    def construct_playlist_url(self):
        """There are two kinds of playlist urls in YouTube. One that contains
        watch?v= in URL, another one contains the "playlist?list=" portion. It
        is preferable to work with the later one.

        :return: playlist url
        """

        if 'watch?v=' in self.playlist_url:
            base_url = 'https://www.youtube.com/playlist?list='
            playlist_code = self.playlist_url.split('&list=')[1]
            return base_url + playlist_code

        # url is already in the desired format, so just return it
        return self.playlist_url

    def _load_more_url(self, req):
        """Given an html page or a fragment thereof, looks for
        and returns the "load more" url if found.
        """
        try:
            load_more_url = 'https://www.youtube.com' + re.search(
                r'data-uix-load-more-href=\"(/browse_ajax\?'
                'action_continuation=.*?)\"', req,
            ).group(1)
        except AttributeError:
            load_more_url = ''
        return load_more_url

    def parse_links(self):
        """Parse the video links from the page source, extracts and
        returns the /watch?v= part from video link href
        It's an alternative for BeautifulSoup
        """

        url = self.construct_playlist_url()
        req = request.get(url)

        # split the page source by line and process each line
        content = [x for x in req.split('\n') if 'pl-video-title-link' in x]
        link_list = [x.split('href="', 1)[1].split('&', 1)[0] for x in content]

        # The above only returns 100 or fewer links
        # Simulating a browser request for the load more link
        load_more_url = self._load_more_url(req)
        while len(load_more_url):   # there is an url found
            logger.debug('load more url: %s' % load_more_url)
            req = request.get(load_more_url)
            load_more = json.loads(req)
            videos = re.findall(
                r'href=\"(/watch\?v=[\w-]*)',
                load_more['content_html'],
            )
            # remove duplicates
            link_list.extend(list(OrderedDict.fromkeys(videos)))
            load_more_url = self._load_more_url(
                load_more['load_more_widget_html'],
            )

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

    def _path_num_prefix_generator(self, reverse=False):
        """
        This generator function generates number prefixes, for the items
        in the playlist.
        If the number of digits required to name a file,is less than is
        required to name the last file,it prepends 0s.
        So if you have a playlist of 100 videos it will number them like:
        001, 002, 003 ect, up to 100.
        It also adds a space after the number.
        :return: prefix string generator : generator
        """
        digits = len(str(len(self.video_urls)))
        if reverse:
            start, stop, step = (len(self.video_urls), 0, -1)
        else:
            start, stop, step = (1, len(self.video_urls) + 1, 1)
        return (str(i).zfill(digits) for i in range(start, stop, step))

    def download_all(
        self,
        download_path=None,
        prefix_number=True,
        reverse_numbering=False,
    ):
        """Download all the videos in the the playlist. Initially, download
        resolution is 720p (or highest available), later more option
        should be added to download resolution of choice

        TODO(nficano): Add option to download resolution of user's choice

        :param download_path:
            (optional) Output path for the playlist If one is not
            specified, defaults to the current working directory.
            This is passed along to the Stream objects.
        :type download_path: str or None
        :param prefix_number:
            (optional) Automatically numbers playlists using the
            _path_num_prefix_generator function.
        :type prefix_number: bool
        :param reverse_numbering:
            (optional) Lets you number playlists in reverse, since some
            playlists are ordered newest -> oldests.
        :type reverse_numbering: bool
        """

        self.populate_video_urls()
        logger.debug('total videos found: %d', len(self.video_urls))
        logger.debug('starting download')

        prefix_gen = self._path_num_prefix_generator(reverse_numbering)

        for link in self.video_urls:
            try:
                yt = YouTube(link)
            except Exception as e:
                logger.debug(e)
                if not self.suppress_exception:
                    raise e
                else:
                    logger.debug('Exception suppressed')
            else:
                # TODO: this should not be hardcoded to a single user's
                # preference
                dl_stream = yt.streams.filter(
                    progressive=True, subtype='mp4',
                ).order_by('resolution').desc().first()

                logger.debug('download path: %s', download_path)
                if prefix_number:
                    prefix = next(prefix_gen)
                    logger.debug('file prefix is: %s', prefix)
                    dl_stream.download(download_path, filename_prefix=prefix)
                else:
                    dl_stream.download(download_path)
                logger.debug('download complete')

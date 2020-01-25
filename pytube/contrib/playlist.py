# -*- coding: utf-8 -*-
"""Module to download a complete playlist from a youtube channel"""

import json
import logging
import re
from collections import OrderedDict
from typing import List, Optional
from urllib.parse import parse_qs

from pytube import request
from pytube.__main__ import YouTube

logger = logging.getLogger(__name__)


class Playlist:
    """Handles all the task of manipulating and downloading a whole YouTube
    playlist
    """

    def __init__(self, url: str, suppress_exception: bool = False):
        self.video_urls: List[str] = []
        self.suppress_exception = suppress_exception
        self.playlist_url: str = url

        if "watch?v=" in url:
            base_url = "https://www.youtube.com/playlist?list="
            query_parameters = parse_qs(url.split("?")[1])
            self.playlist_url = base_url + query_parameters["list"][0]

    @staticmethod
    def _find_load_more_url(req: str) -> Optional[str]:
        """Given an html page or a fragment thereof, looks for
        and returns the "load more" url if found.
        """
        match = re.search(
            r"data-uix-load-more-href=\"(/browse_ajax\?" 'action_continuation=.*?)"',
            req,
        )
        if match:
            return "https://www.youtube.com" + match.group(1)

        return None

    def parse_links(self) -> List[str]:
        """Parse the video links from the page source, extracts and
        returns the /watch?v= part from video link href
        It's an alternative for BeautifulSoup
        """

        req = request.get(self.playlist_url)

        # split the page source by line and process each line
        content = [x for x in req.split("\n") if "pl-video-title-link" in x]
        link_list = [x.split('href="', 1)[1].split("&", 1)[0] for x in content]

        # The above only returns 100 or fewer links
        # Simulating a browser request for the load more link
        load_more_url = self._find_load_more_url(req)
        while load_more_url:  # there is an url found
            logger.debug("load more url: %s", load_more_url)
            req = request.get(load_more_url)
            load_more = json.loads(req)
            videos = re.findall(
                r"href=\"(/watch\?v=[\w-]*)", load_more["content_html"],
            )
            # remove duplicates
            link_list.extend(list(OrderedDict.fromkeys(videos)))
            load_more_url = self._find_load_more_url(
                load_more["load_more_widget_html"],
            )

        return link_list

    def populate_video_urls(self) -> None:
        """Construct complete links of all the videos in playlist and
        populate video_urls list

        :return: urls -> string
        """

        base_url = "https://www.youtube.com"
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
        download_path: Optional[str] = None,
        prefix_number: bool = True,
        reverse_numbering: bool = False,
        resolution: str = "720p",
    ) -> None:
        """Download all the videos in the the playlist. Initially, download
        resolution is 720p (or highest available), later more option
        should be added to download resolution of choice

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
            playlists are ordered newest -> oldest.
        :type reverse_numbering: bool
        :param resolution:
            Video resolution i.e. "720p", "480p", "360p", "240p", "144p"
        :type resolution: str
        """

        self.populate_video_urls()
        logger.debug("total videos found: %d", len(self.video_urls))
        logger.debug("starting download")

        prefix_gen = self._path_num_prefix_generator(reverse_numbering)

        for link in self.video_urls:
            try:
                yt = YouTube(link)
            except Exception as e:
                logger.debug(e)
                if not self.suppress_exception:
                    raise e
            else:
                dl_stream = (
                    yt.streams.get_by_resolution(resolution=resolution)
                    or yt.streams.get_lowest_resolution()
                )
                assert dl_stream is not None

                logger.debug("download path: %s", download_path)
                if prefix_number:
                    prefix = next(prefix_gen)
                    logger.debug("file prefix is: %s", prefix)
                    dl_stream.download(download_path, filename_prefix=prefix)
                else:
                    dl_stream.download(download_path)
                logger.debug("download complete")

    def title(self) -> Optional[str]:
        """return playlist title (name)"""
        req = request.get(self.playlist_url)
        open_tag = "<title>"
        end_tag = "</title>"
        pattern = re.compile(open_tag + "(.+?)" + end_tag)
        match = pattern.search(req)

        if match is None:
            return None

        return (
            match.group()
            .replace(open_tag, "")
            .replace(end_tag, "")
            .replace("- YouTube", "")
            .strip()
        )

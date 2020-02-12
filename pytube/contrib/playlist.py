# -*- coding: utf-8 -*-

"""Module to download a complete playlist from a youtube channel."""

import json
import logging
import re
from datetime import date, datetime
from typing import List, Optional, Iterable, Dict, Union
from urllib.parse import parse_qs
from collections.abc import Sequence

from pytube import request, YouTube
from pytube.helpers import cache, deprecated, install_proxy, uniqueify

logger = logging.getLogger(__name__)


class Playlist(Sequence):
    """Load a YouTube playlist with URL or ID"""

    def __init__(self, url: str, proxies: Optional[Dict[str, str]] = None):
        if proxies:
            install_proxy(proxies)

        try:
            self.playlist_id: str = parse_qs(url.split("?")[1])["list"][0]
        except IndexError:  # assume that url is just the id
            self.playlist_id = url

        self.playlist_url = f"https://www.youtube.com/playlist?list={self.playlist_id}"
        self.html = request.get(self.playlist_url)

        # Needs testing with non-English
        self.last_update: Optional[date] = None
        date_match = re.search(
            r"<li>Last updated on (\w{3}) (\d{1,2}), (\d{4})</li>", self.html
        )
        if date_match:
            month, day, year = date_match.groups()
            self.last_update = datetime.strptime(
                f"{month} {day:0>2} {year}", "%b %d %Y"
            ).date()

        self._video_regex = re.compile(r"href=\"(/watch\?v=[\w-]*)")

    @staticmethod
    def _find_load_more_url(req: str) -> Optional[str]:
        """Given an html page or fragment, returns the "load more" url if found."""
        match = re.search(
            r"data-uix-load-more-href=\"(/browse_ajax\?" 'action_continuation=.*?)"',
            req,
        )
        if match:
            return f"https://www.youtube.com{match.group(1)}"

        return None

    @deprecated("This function will be removed in the future, please use .video_urls")
    def parse_links(self) -> List[str]:  # pragma: no cover
        """ Deprecated function for returning list of URLs

        :return: List[str]
        """
        return self.video_urls

    def _paginate(self, until_watch_id: Optional[str] = None) -> Iterable[List[str]]:
        """Parse the video links from the page source, yields the /watch?v= part from video link
        """
        req = self.html
        videos_urls = self._extract_videos(req)
        if until_watch_id:
            try:
                trim_index = videos_urls.index(f"/watch?v={until_watch_id}")
                yield videos_urls[:trim_index]
                return
            except ValueError:
                pass
        yield videos_urls

        # The above only returns 100 or fewer links
        # Simulating a browser request for the load more link
        load_more_url = self._find_load_more_url(req)

        while load_more_url:  # there is an url found
            logger.debug("load more url: %s", load_more_url)
            req = request.get(load_more_url)
            load_more = json.loads(req)
            try:
                html = load_more["content_html"]
            except KeyError:
                logger.debug("Could not find content_html")
                return
            videos_urls = self._extract_videos(html)
            if until_watch_id:
                try:
                    trim_index = videos_urls.index(f"/watch?v={until_watch_id}")
                    yield videos_urls[:trim_index]
                    return
                except ValueError:
                    pass
            yield videos_urls

            load_more_url = self._find_load_more_url(
                load_more["load_more_widget_html"],
            )

        return

    def _extract_videos(self, html: str) -> List[str]:
        return uniqueify(self._video_regex.findall(html))

    def trimmed(self, video_id: str) -> Iterable[str]:
        """Retrieve a list of YouTube video URLs trimmed at the given video ID

        i.e. if the playlist has video IDs 1,2,3,4 calling trimmed(3) returns [1,2]
        :type video_id: str
            video ID to trim the returned list of playlist URLs at
        :rtype: List[str]
        :returns:
            List of video URLs from the playlist trimmed at the given ID
        """
        for page in self._paginate(until_watch_id=video_id):
            yield from (self._video_url(watch_path) for watch_path in page)

    @property  # type: ignore
    @cache
    def video_urls(self) -> List[str]:
        """Complete links of all the videos in playlist

        :rtype: List[str]
        :returns: List of video URLs
        """
        return [
            self._video_url(video) for page in list(self._paginate()) for video in page
        ]

    @property
    def videos(self) -> Iterable[YouTube]:
        """Yields YouTube objects of videos in this playlist

        :Yields: YouTube
        """
        yield from (YouTube(url) for url in self.video_urls)

    def __getitem__(self, i: Union[slice, int]) -> Union[str, List[str]]:
        return self.video_urls[i]

    def __len__(self) -> int:
        return len(self.video_urls)

    def __repr__(self) -> str:
        return f"{self.video_urls}"

    @deprecated(
        "This call is unnecessary, you can directly access .video_urls or .videos"
    )
    def populate_video_urls(self) -> List[str]:  # pragma: no cover
        """Complete links of all the videos in playlist

        :rtype: List[str]
        :returns: List of video URLs
        """
        return self.video_urls

    @deprecated("This function will be removed in the future.")
    def _path_num_prefix_generator(self, reverse=False):  # pragma: no cover
        """Generate number prefixes for the items in the playlist.

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

    @deprecated(
        "This function will be removed in the future. Please iterate through .videos"
    )
    def download_all(
        self,
        download_path: Optional[str] = None,
        prefix_number: bool = True,
        reverse_numbering: bool = False,
        resolution: str = "720p",
    ) -> None:  # pragma: no cover
        """Download all the videos in the the playlist.

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
        logger.debug("total videos found: %d", len(self.video_urls))
        logger.debug("starting download")

        prefix_gen = self._path_num_prefix_generator(reverse_numbering)

        for link in self.video_urls:
            youtube = YouTube(link)
            dl_stream = (
                youtube.streams.get_by_resolution(resolution=resolution)
                or youtube.streams.get_lowest_resolution()
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

    @cache
    def title(self) -> Optional[str]:
        """Extract playlist title

        :return: playlist title (name)
        :rtype: Optional[str]
        """
        pattern = re.compile("<title>(.+?)</title>")
        match = pattern.search(self.html)

        if match is None:
            return None

        return match.group(1).replace("- YouTube", "").strip()

    @staticmethod
    def _video_url(watch_path: str):
        return f"https://www.youtube.com{watch_path}"

"""Module to download a complete playlist from a youtube channel."""
import json
import logging
from collections.abc import Sequence
from datetime import date, datetime
from typing import Dict, Iterable, List, Optional, Tuple, Union

from pytube import extract, request, YouTube
from pytube.helpers import cache, DeferredGeneratorList, install_proxy, uniqueify

logger = logging.getLogger(__name__)


class Playlist(Sequence):
    """Load a YouTube playlist with URL"""

    def __init__(self, url: str, proxies: Optional[Dict[str, str]] = None):
        if proxies:
            install_proxy(proxies)

        self._input_url = url

        # These need to be initialized as None for the properties.
        self._html = None
        self._ytcfg = None
        self._initial_data = None
        self._sidebar_info = None

        self._playlist_id = None

    @property
    def playlist_id(self):
        """Get the playlist id.

        :rtype: str
        """
        if self._playlist_id:
            return self._playlist_id
        self._playlist_id = extract.playlist_id(self._input_url)
        return self._playlist_id

    @property
    def playlist_url(self):
        """Get the base playlist url.

        :rtype: str
        """
        return f"https://www.youtube.com/playlist?list={self.playlist_id}"

    @property
    def html(self):
        """Get the playlist page html.

        :rtype: str
        """
        if self._html:
            return self._html
        self._html = request.get(self.playlist_url)
        return self._html

    @property
    def ytcfg(self):
        """Extract the ytcfg from the playlist page html.

        :rtype: dict
        """
        if self._ytcfg:
            return self._ytcfg
        self._ytcfg = extract.get_ytcfg(self.html)
        return self._ytcfg

    @property
    def initial_data(self):
        """Extract the initial data from the playlist page html.

        :rtype: dict
        """
        if self._initial_data:
            return self._initial_data
        else:
            self._initial_data = extract.initial_data(self.html)
            return self._initial_data

    @property
    def sidebar_info(self):
        """Extract the sidebar info from the playlist page html.

        :rtype: dict
        """
        if self._sidebar_info:
            return self._sidebar_info
        else:
            self._sidebar_info = self.initial_data['sidebar'][
                'playlistSidebarRenderer']['items']
            return self._sidebar_info

    @property
    def yt_api_key(self):
        """Extract the INNERTUBE_API_KEY from the playlist ytcfg.

        :rtype: str
        """
        return self.ytcfg['INNERTUBE_API_KEY']

    def _paginate(
        self, until_watch_id: Optional[str] = None
    ) -> Iterable[List[str]]:
        """Parse the video links from the page source, yields the /watch?v=
        part from video link

        :param until_watch_id Optional[str]: YouTube Video watch id until
            which the playlist should be read.

        :rtype: Iterable[List[str]]
        :returns: Iterable of lists of YouTube watch ids
        """
        videos_urls, continuation = self._extract_videos(
            json.dumps(extract.initial_data(self.html))
        )
        if until_watch_id:
            try:
                trim_index = videos_urls.index(f"/watch?v={until_watch_id}")
                yield videos_urls[:trim_index]
                return
            except ValueError:
                pass
        yield videos_urls

        # Extraction from a playlist only returns 100 videos at a time
        # if self._extract_videos returns a continuation there are more
        # than 100 songs inside a playlist, so we need to add further requests
        # to gather all of them
        if continuation:
            load_more_url, headers, data = self._build_continuation_url(continuation)
        else:
            load_more_url, headers, data = None, None, None

        while load_more_url and headers and data:  # there is an url found
            logger.debug("load more url: %s", load_more_url)
            # requesting the next page of videos with the url generated from the
            # previous page, needs to be a post
            req = request.post(load_more_url, extra_headers=headers, data=data)
            # extract up to 100 songs from the page loaded
            # returns another continuation if more videos are available
            videos_urls, continuation = self._extract_videos(req)
            if until_watch_id:
                try:
                    trim_index = videos_urls.index(f"/watch?v={until_watch_id}")
                    yield videos_urls[:trim_index]
                    return
                except ValueError:
                    pass
            yield videos_urls

            if continuation:
                load_more_url, headers, data = self._build_continuation_url(
                    continuation
                )
            else:
                load_more_url, headers, data = None, None, None

    def _build_continuation_url(self, continuation: str) -> Tuple[str, dict, dict]:
        """Helper method to build the url and headers required to request
        the next page of videos

        :param str continuation: Continuation extracted from the json response
            of the last page
        :rtype: Tuple[str, dict, dict]
        :returns: Tuple of an url and required headers for the next http
            request
        """
        return (
            (
                # was changed to this format (and post requests)
                # between 2021.03.02 and 2021.03.03
                "https://www.youtube.com/youtubei/v1/browse?key="
                f"{self.yt_api_key}"
            ),
            {
                "X-YouTube-Client-Name": "1",
                "X-YouTube-Client-Version": "2.20200720.00.02",
            },
            # extra data required for post request
            {
                "continuation": continuation,
                "context": {
                    "client": {
                        "clientName": "WEB",
                        "clientVersion": "2.20200720.00.02"
                    }
                }
            }
        )

    @staticmethod
    def _extract_videos(raw_json: str) -> Tuple[List[str], Optional[str]]:
        """Extracts videos from a raw json page

        :param str raw_json: Input json extracted from the page or the last
            server response
        :rtype: Tuple[List[str], Optional[str]]
        :returns: Tuple containing a list of up to 100 video watch ids and
            a continuation token, if more videos are available
        """
        initial_data = json.loads(raw_json)
        try:
            # this is the json tree structure, if the json was extracted from
            # html
            section_contents = initial_data["contents"][
                "twoColumnBrowseResultsRenderer"][
                "tabs"][0]["tabRenderer"]["content"][
                "sectionListRenderer"]["contents"]
            try:
                # Playlist without submenus
                important_content = section_contents[
                    0]["itemSectionRenderer"][
                    "contents"][0]["playlistVideoListRenderer"]
            except (KeyError, IndexError, TypeError):
                # Playlist with submenus
                important_content = section_contents[
                    1]["itemSectionRenderer"][
                    "contents"][0]["playlistVideoListRenderer"]
            videos = important_content["contents"]
        except (KeyError, IndexError, TypeError):
            try:
                # this is the json tree structure, if the json was directly sent
                # by the server in a continuation response
                # no longer a list and no longer has the "response" key
                important_content = initial_data['onResponseReceivedActions'][0][
                    'appendContinuationItemsAction']['continuationItems']
                videos = important_content
            except (KeyError, IndexError, TypeError) as p:
                logger.info(p)
                return [], None

        try:
            continuation = videos[-1]['continuationItemRenderer'][
                'continuationEndpoint'
            ]['continuationCommand']['token']
            videos = videos[:-1]
        except (KeyError, IndexError):
            # if there is an error, no continuation is available
            continuation = None

        # remove duplicates
        return (
            uniqueify(
                list(
                    # only extract the video ids from the video data
                    map(
                        lambda x: (
                            f"/watch?v="
                            f"{x['playlistVideoRenderer']['videoId']}"
                        ),
                        videos
                    )
                ),
            ),
            continuation,
        )

    def trimmed(self, video_id: str) -> Iterable[str]:
        """Retrieve a list of YouTube video URLs trimmed at the given video ID

        i.e. if the playlist has video IDs 1,2,3,4 calling trimmed(3) returns
        [1,2]
        :type video_id: str
            video ID to trim the returned list of playlist URLs at
        :rtype: List[str]
        :returns:
            List of video URLs from the playlist trimmed at the given ID
        """
        for page in self._paginate(until_watch_id=video_id):
            yield from (self._video_url(watch_path) for watch_path in page)

    def url_generator(self):
        """Generator that yields video URLs.

        :Yields: Video URLs
        """
        for page in self._paginate():
            for video in page:
                yield self._video_url(video)

    @property  # type: ignore
    @cache
    def video_urls(self) -> DeferredGeneratorList:
        """Complete links of all the videos in playlist

        :rtype: List[str]
        :returns: List of video URLs
        """
        return DeferredGeneratorList(self.url_generator())

    def videos_generator(self):
        for url in self.video_urls:
            yield YouTube(url)

    @property
    def videos(self) -> Iterable[YouTube]:
        """Yields YouTube objects of videos in this playlist

        :rtype: List[YouTube]
        :returns: List of YouTube
        """
        return DeferredGeneratorList(self.videos_generator())

    def __getitem__(self, i: Union[slice, int]) -> Union[str, List[str]]:
        return self.video_urls[i]

    def __len__(self) -> int:
        return len(self.video_urls)

    def __repr__(self) -> str:
        return f"{repr(self.video_urls)}"

    @property
    @cache
    def last_updated(self) -> Optional[date]:
        """Extract the date that the playlist was last updated.

        For some playlists, this will be a specific date, which is returned as a datetime
        object. For other playlists, this is an estimate such as "1 week ago". Due to the
        fact that this value is returned as a string, pytube does a best-effort parsing
        where possible, and returns the raw string where it is not possible.

        :return: Date of last playlist update where possible, else the string provided
        :rtype: datetime.date
        """
        last_updated_text = self.sidebar_info[0]['playlistSidebarPrimaryInfoRenderer'][
            'stats'][2]['runs'][1]['text']
        try:
            date_components = last_updated_text.split()
            month = date_components[0]
            day = date_components[1].strip(',')
            year = date_components[2]
            return datetime.strptime(
                f"{month} {day:0>2} {year}", "%b %d %Y"
            ).date()
        except (IndexError, KeyError):
            return last_updated_text

    @property
    @cache
    def title(self) -> Optional[str]:
        """Extract playlist title

        :return: playlist title (name)
        :rtype: Optional[str]
        """
        return self.sidebar_info[0]['playlistSidebarPrimaryInfoRenderer'][
            'title']['runs'][0]['text']

    @property
    def description(self) -> str:
        return self.sidebar_info[0]['playlistSidebarPrimaryInfoRenderer'][
            'description']['simpleText']

    @property
    def length(self):
        """Extract the number of videos in the playlist.

        :return: Playlist video count
        :rtype: int
        """
        count_text = self.sidebar_info[0]['playlistSidebarPrimaryInfoRenderer'][
            'stats'][0]['runs'][0]['text']
        count_text = count_text.replace(',','')
        return int(count_text)

    @property
    def views(self):
        """Extract view count for playlist.

        :return: Playlist view count
        :rtype: int
        """
        # "1,234,567 views"
        views_text = self.sidebar_info[0]['playlistSidebarPrimaryInfoRenderer'][
            'stats'][1]['simpleText']
        # "1,234,567"
        count_text = views_text.split()[0]
        # "1234567"
        count_text = count_text.replace(',', '')
        return int(count_text)

    @property
    def owner(self):
        """Extract the owner of the playlist.

        :return: Playlist owner name.
        :rtype: str
        """
        return self.sidebar_info[1]['playlistSidebarSecondaryInfoRenderer'][
            'videoOwner']['videoOwnerRenderer']['title']['runs'][0]['text']

    @property
    def owner_id(self):
        """Extract the channel_id of the owner of the playlist.

        :return: Playlist owner's channel ID.
        :rtype: str
        """
        return self.sidebar_info[1]['playlistSidebarSecondaryInfoRenderer'][
            'videoOwner']['videoOwnerRenderer']['title']['runs'][0][
            'navigationEndpoint']['browseEndpoint']['browseId']

    @property
    def owner_url(self):
        """Create the channel url of the owner of the playlist.

        :return: Playlist owner's channel url.
        :rtype: str
        """
        return f'https://www.youtube.com/channel/{self.owner_id}'

    @staticmethod
    def _video_url(watch_path: str):
        return f"https://www.youtube.com{watch_path}"

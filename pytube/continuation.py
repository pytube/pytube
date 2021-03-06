import json, logging

from pytube import request
from pytube import extract

from typing import Iterable, List, Optional, Tuple

logger = logging.getLogger(__name__)

class Continuation:
    def __init__(self, extractor_class, initial_html):
        self.fully_cached = False
        self.list_cache = []
        self.extractor_class = extractor_class
        self.gen = self._paginate(initial_html)
        ...

    def __iter__(self):
        self.n = 0
        return self

    def __next__(self):
        # We iterate over all items via indexing.
        while True:
            try:
                return self[self.n]
            except IndexError:
                raise StopIteration
            else:
                self.n += 1

    def __getitem__(self, key):
        if type(key) is not int:
            raise TypeError
        if key < len(self.list_cache):
            return self.list_cache[key]
        # Generate as necessary until we find the key or end
        while key >= len(self.list_cache):
            try:
                next(self.gen)
            except StopIteration:
                raise IndexError
        return self.list_cache[key]

    def _paginate(self, initial_html) -> Iterable[List[str]]:
        """Parse the video links from the page source, yields the /watch?v=
        part from video link

        :param until_watch_id Optional[str]: YouTube Video watch id until
            which the playlist should be read.

        :rtype: Iterable[List[str]]
        :returns: Iterable of lists of YouTube watch ids
        """
        videos_urls, continuation = self.extractor_class._extract_videos(
            json.dumps(extract.initial_data(initial_html))
        )
        self.list_cache = videos_urls
        yield videos_urls

        # Extraction from a playlist only returns 100 videos at a time
        # if self._extract_videos returns a continuation there are more
        # than 100 songs inside a playlist, so we need to add further requests
        # to gather all of them
        if continuation:
            load_more_url, headers = self._build_continuation_url(continuation)
        else:
            load_more_url, headers = None, None

        while load_more_url and headers:  # there is an url found
            logger.debug("load more url: %s", load_more_url)
            # requesting the next page of videos with the url generated from the
            # previous page
            req = request.get(load_more_url, extra_headers=headers)
            # extract up to 100 songs from the page loaded
            # returns another continuation if more videos are available
            videos_urls, continuation = self.extractor_class._extract_videos(req)
            self.list_cache = videos_urls
            yield videos_urls

            if continuation:
                load_more_url, headers = self._build_continuation_url(
                    continuation
                )
            else:
                load_more_url, headers = None, None

    @staticmethod
    def _build_continuation_url(continuation: str) -> Tuple[str, dict]:
        """Helper method to build the url and headers required to request
        the next page of videos

        :param str continuation: Continuation extracted from the json response
            of the last page
        :rtype: Tuple[str, dict]
        :returns: Tuple of an url and required headers for the next http
            request
        """
        return (
            (
                f"https://www.youtube.com/browse_ajax?ctoken="
                f"{continuation}&continuation={continuation}"
            ),
            {
                "X-YouTube-Client-Name": "1",
                "X-YouTube-Client-Version": "2.20200720.00.02",
            },
        )
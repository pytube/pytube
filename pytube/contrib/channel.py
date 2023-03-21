# -*- coding: utf-8 -*-
"""Module for interacting with a user's youtube channel."""
import json
import logging
from typing import Dict, List, Optional, Tuple

from datetime import datetime
from urllib.parse import unquote
from re import findall

from pytube import extract, Playlist, request
from pytube.helpers import uniqueify

logger = logging.getLogger(__name__)


class Channel(Playlist):
    def __init__(self, url: str, proxies: Optional[Dict[str, str]] = None):
        """Construct a :class:`Channel <Channel>`.

        :param str url:
            A valid YouTube channel URL.
        :param proxies:
            (Optional) A dictionary of proxies to use for web requests.
        """
        super().__init__(url, proxies)

        self.channel_uri = extract.channel_name(url)

        self.channel_url = (
            f"https://www.youtube.com{self.channel_uri}"
        )

        self.videos_url = self.channel_url + '/videos'
        self.playlists_url = self.channel_url + '/playlists'
        self.community_url = self.channel_url + '/community'
        self.featured_channels_url = self.channel_url + '/channels'
        self.about_url = self.channel_url + '/about'

        # Possible future additions
        self._playlists_html = None
        self._community_html = None
        self._featured_channels_html = None
        self._about_html = None
        
        self._about_page_initial_data = None

    @property
    def channel_name(self):
        """Get the name of the YouTube channel.

        :rtype: str
        """
        return self.initial_data['metadata']['channelMetadataRenderer']['title']

    @property
    def channel_id(self):
        """Get the ID of the YouTube channel.

        This will return the underlying ID, not the vanity URL.

        :rtype: str
        """
        return self.initial_data['metadata']['channelMetadataRenderer']['externalId']

    @property
    def vanity_url(self):
        """Get the vanity URL of the YouTube channel.

        Returns None if it doesn't exist.

        :rtype: str
        """
        return self.initial_data['metadata']['channelMetadataRenderer'].get('vanityChannelUrl', None)  # noqa:E501

    @property
    def html(self):
        """Get the html for the /videos page.

        :rtype: str
        """
        if self._html:
            return self._html
        self._html = request.get(self.videos_url)
        return self._html

    @property
    def playlists_html(self):
        """Get the html for the /playlists page.

        Currently unused for any functionality.

        :rtype: str
        """
        if self._playlists_html:
            return self._playlists_html
        else:
            self._playlists_html = request.get(self.playlists_url)
            return self._playlists_html

    @property
    def community_html(self):
        """Get the html for the /community page.

        Currently unused for any functionality.

        :rtype: str
        """
        if self._community_html:
            return self._community_html
        else:
            self._community_html = request.get(self.community_url)
            return self._community_html

    @property
    def featured_channels_html(self):
        """Get the html for the /channels page.

        Currently unused for any functionality.

        :rtype: str
        """
        if self._featured_channels_html:
            return self._featured_channels_html
        else:
            self._featured_channels_html = request.get(self.featured_channels_url)
            return self._featured_channels_html

    @property
    def about_html(self):
        """Get the html for the /about page.

        Currently unused for any functionality.

        :rtype: str
        """
        if self._about_html:
            return self._about_html
        else:
            self._about_html = request.get(self.about_url)
            return self._about_html

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
        # this is the json tree structure, if the json was extracted from
        # html
        try:
            videos = initial_data["contents"][
                "twoColumnBrowseResultsRenderer"][
                "tabs"][1]["tabRenderer"]["content"][
                "richGridRenderer"]["contents"]
        except (KeyError, IndexError, TypeError):
            try:
                # this is the json tree structure, if the json was directly sent
                # by the server in a continuation response
                important_content = initial_data[1]['response']['onResponseReceivedActions'][
                    0
                ]['appendContinuationItemsAction']['continuationItems']
                videos = important_content
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
                            f"{x['richItemRenderer']['content']['videoRenderer']['videoId']}"
                        ),
                        videos
                    )
                ),
            ),
            continuation,
        )



    @property
    def is_a_verified_channel(self) -> bool:
        """Get the the verified badge status of the YouTube channel.

        :rtype: bool
        """
        try:
            _is_a_verified_channel= self.initial_data["header"]["c4TabbedHeaderRenderer"]["badges"][0]["metadataBadgeRenderer"]["tooltip"] == "Verified"
        except KeyError:
            _is_a_verified_channel = False
        return _is_a_verified_channel
    
    @property
    def banner_thumbnail(self) -> Optional[str]:
        """Get the banner thumbnail of the YouTube channel.

        :rtype: Optional[str]
        """
        try:
            _banner_thumbnail = self.initial_data["header"]["c4TabbedHeaderRenderer"]["banner"]["thumbnails"][-1]["url"]
        except KeyError:
            _banner_thumbnail = None
        return _banner_thumbnail    
    
    @property
    def avatar_thumbnail(self) -> Optional[str]:
        """Get the avatar thumbnail of the YouTube channel.

        :rtype: Optional[str]
        """
        try:
            _avatar_thumbnail = self.initial_data["metadata"]["channelMetadataRenderer"]["avatar"]["thumbnails"][-1]["url"]
        except KeyError:
            _avatar_thumbnail = None
        return _avatar_thumbnail    
    
    @property
    def description(self) -> Optional[str]:
        """Get the description of the YouTube channel.

        :rtype: Optional[str]
        """
        try:
            _description = self.initial_data["metadata"]["channelMetadataRenderer"]["description"]       
        except KeyError:
            _description = None
        return _description
        
    @property
    def urls_present_in_the_channel_description(self) -> List[str]:
        """Get the Urls present in the channel description of the YouTube channel.

        :rtype: List[str]
        """                
        pattern = "https?:\\/\\/(?:www\\.)?[-a-zA-Z0-9@:%._\\+~#=]{1,256}\\.[a-zA-Z0-9()]{1,6}\\b(?:[-a-zA-Z0-9()@:%_\\+.~#?&\\/=]*)"         
        return list(set(findall(pattern, self.description)))    
           
    @property
    def mails_present_in_the_channel_description(self) -> List[str]:
        """Get the Mails present in the channel description of the YouTube channel.

        :rtype: List[str]
        """                 
        pattern = r"\S+@\S+\.\S+"             
        _mails = [mail for mail in list(set(findall(pattern, self.description))) if not mail.startswith("http")]         
        return _mails
     
    @property
    def keywords(self) -> Optional[str]:
        """Get the description of the YouTube channel.

        :rtype: Optional[str]
        """
        try:
            _keywords = self.initial_data["microformat"]["microformatDataRenderer"]["tags"]
        except KeyError:
            _keywords = None
        return _keywords
    
    @property
    def about_page_initial_data(self):
        """Get the initial data for the /about page.

        Currently unused for any functionality.

        :rtype: dict
        """
        if not self._about_page_initial_data:
            self._about_page_initial_data = extract.initial_data(self.about_html)
        return self._about_page_initial_data
       
    @property
    def joined_date(self) -> str:
        """Get the joined date of the YouTube channel.

        :rtype: str
        """        
        try:
            _joined_date = self.about_page_initial_data["contents"]["twoColumnBrowseResultsRenderer"]["tabs"][-2]["tabRenderer"]["content"]["sectionListRenderer"]["contents"][0]["itemSectionRenderer"]["contents"][0]["channelAboutFullMetadataRenderer"]["joinedDateText"]["runs"][-1]["text"]
            _joined_date = str(datetime.strptime(_joined_date, '%b %d, %Y').date())
        except KeyError:
            _joined_date = None
        return _joined_date    
    
    @property
    def channel_views(self) -> int:
        """Get the number of views of the YouTube channel.

        :rtype: int
        """        
        try:
            _channel_views = self.about_page_initial_data["contents"]["twoColumnBrowseResultsRenderer"]["tabs"][-2]["tabRenderer"]["content"]["sectionListRenderer"]["contents"][0]["itemSectionRenderer"]["contents"][0]["channelAboutFullMetadataRenderer"]["viewCountText"]["simpleText"]
            _channel_views = int(_channel_views.replace(",", "").replace(" views", ""))
        except KeyError:
            _channel_views = None
        return _channel_views    
    
    @property
    def country(self) -> str:
        """Get the country of the YouTube channel.

        :rtype: str
        """        
        try:
            _country = self.about_page_initial_data["contents"]["twoColumnBrowseResultsRenderer"]["tabs"][-2]["tabRenderer"]["content"]["sectionListRenderer"]["contents"][0]["itemSectionRenderer"]["contents"][0]["channelAboutFullMetadataRenderer"]["country"]["simpleText"]
        except KeyError:
            _country = None
        return _country    
    
    @property
    def social_links(self) -> dict:
        """Get the social links of the YouTube channel.

        :rtype: dict
        """
        social_links_dict = {}
        try:
            social_links = self.about_page_initial_data["contents"]["twoColumnBrowseResultsRenderer"]["tabs"][-2]["tabRenderer"]["content"]["sectionListRenderer"]["contents"][0]["itemSectionRenderer"]["contents"][0]["channelAboutFullMetadataRenderer"]['primaryLinks']
            for social_link in social_links:
                k = social_link["title"]["simpleText"]
                v = unquote(social_link["navigationEndpoint"]["urlEndpoint"]["url"].split("=")[-1])
                social_links_dict[k] = v
        except KeyError:
            social_links_dict = None
        return social_links_dict    
    
    @property
    def subscribers(self) -> int:
        """Get the number of subscribers of the YouTube channel.

        :rtype: int
        """
        try:
            _subscribers = self.initial_data["header"]["c4TabbedHeaderRenderer"]["subscriberCountText"]["simpleText"].replace(" subscribers", "")     
            _subscribers = _subscribers.replace("K", "e3").replace("M", "e6").replace("No", "0")  
            _subscribers = int(float(_subscribers))    
        except KeyError:
            _subscribers = None
        return _subscribers
       
    @property
    def channel_type(self) -> str:
        """Get the type of the YouTube channel.
        
        Not implemented yet

        :rtype: str
        """
        try:
            _channel_type = None   
        except KeyError:
            _channel_type = None
        return _channel_type
   

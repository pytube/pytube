"""This module is designed to interact with the innertube API.

This module is NOT intended to be used directly by end users, as each of the
interfaces returns raw results. These should instead be parsed to extract
the useful information for the end user.
"""
# Native python imports
import json
from urllib import parse

# Local imports
from pytube import request


class InnerTube:
    """Object for interacting with the innertube API."""
    @property
    def base_url(self):
        """Return the base url endpoint for the innertube API."""
        return 'https://www.youtube.com/youtubei/v1'

    @property
    def base_data(self):
        """Return the base json data to transmit to the innertube API."""
        return {
            'context': {
                'client': {
                    'clientName': 'WEB',
                    'clientVersion': '2.20200720.00.02'
                }
            }
        }

    @property
    def base_params(self):
        """Return the base query parameters to transmit to the innertube API."""
        return {
            'key': 'AIzaSyAO_FJ2SlqU8Q4STEHLGCilw_Y9_11qcW8'
        }

    def _call_api(self, endpoint, query, data):
        """Make a request to a given endpoint with the provided query parameters and data."""
        endpoint_url = f'{endpoint}?{parse.urlencode(query)}'
        response = request._execute_request(
            endpoint_url,
            'POST',
            headers={
                'Content-Type': 'application/json',
            },
            data=data
        )
        return json.loads(response.read())

    def browse(self):
        """Make a request to the browse endpoint.

        TODO: Figure out how we can use this
        """
        # endpoint = f'{self.base_url}/browse'  # noqa:E800
        ...
        # return self._call_api(endpoint, query, self.base_data)  # noqa:E800

    def config(self):
        """Make a request to the config endpoint.

        TODO: Figure out how we can use this
        """
        # endpoint = f'{self.base_url}/config'  # noqa:E800
        ...
        # return self._call_api(endpoint, query, self.base_data)  # noqa:E800

    def guide(self):
        """Make a request to the guide endpoint.

        TODO: Figure out how we can use this
        """
        # endpoint = f'{self.base_url}/guide'  # noqa:E800
        ...
        # return self._call_api(endpoint, query, self.base_data)  # noqa:E800

    def next(self):
        """Make a request to the next endpoint.

        TODO: Figure out how we can use this
        """
        # endpoint = f'{self.base_url}/next'  # noqa:E800
        ...
        # return self._call_api(endpoint, query, self.base_data)  # noqa:E800

    def player(self, video_id):
        """Make a request to the player endpoint.

        :param str video_id:
            The video id to get player info for.
        :rtype: dict
        :returns:
            Raw player info results.
        """
        endpoint = f'{self.base_url}/player'
        query = {
            'videoId': video_id,
        }
        query.update(self.base_params)
        return self._call_api(endpoint, query, self.base_data)

    def search(self, search_query, continuation=None):
        """Make a request to the search endpoint.

        :param str search_query:
            The query to search.
        :rtype: dict
        :returns:
            Raw search query results.
        """
        endpoint = f'{self.base_url}/search'
        query = {
            'query': search_query
        }
        query.update(self.base_params)
        data = {}
        if continuation:
            data['continuation'] = continuation
        data.update(self.base_data)
        return self._call_api(endpoint, query, data)

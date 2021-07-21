"""This module is designed to interact with the innertube API.

This module is NOT intended to be used directly by end users, as each of the
interfaces returns raw results. These should instead be parsed to extract
the useful information for the end user.
"""
# Native python imports
from datetime import datetime
import json
from urllib import parse

# Local imports
from pytube import request


_default_clients = {
    'WEB': {
        'context': {
            'client': {
                'clientName': 'WEB',
                'clientVersion': '2.20200720.00.02'
            }
        },
        'api_key': 'AIzaSyAO_FJ2SlqU8Q4STEHLGCilw_Y9_11qcW8'
    },
    'ANDROID': {
        'context': {
            'client': {
                'clientName': 'ANDROID',
                'clientVersion': '16.20'
            }
        },
        'api_key': 'AIzaSyAO_FJ2SlqU8Q4STEHLGCilw_Y9_11qcW8'
    }
}
_token_timeout = 1800


class InnerTube:
    """Object for interacting with the innertube API."""
    def __init__(self, client='WEB', bearer_token=None):
        self.context = _default_clients[client]['context']
        self.api_key = _default_clients[client]['api_key']
        self.bearer_token = bearer_token
        self.last_refresh = None
        self.refresh_bearer_token()

    def refresh_bearer_token(self, force=False):
        """Refreshes the OAuth token.

        This is skeleton code for potential future functionality, so it is incomplete.
        """
        # Skip refresh if it's been less than 30 minutes
        if self.last_refresh and not force:
            # Use a 30-minute timer.
            if (datetime.now() - self.last_refresh).total_seconds() < _token_timeout:
                return

        # TODO: Refresh the token

        self.last_refresh = datetime.now()

    @property
    def base_url(self):
        """Return the base url endpoint for the innertube API."""
        return 'https://www.youtube.com/youtubei/v1'

    @property
    def base_data(self):
        """Return the base json data to transmit to the innertube API."""
        return {
            'context': self.context
        }

    @property
    def base_params(self):
        """Return the base query parameters to transmit to the innertube API."""
        return {
            'key': self.api_key
        }

    def _call_api(self, endpoint, query, data):
        """Make a request to a given endpoint with the provided query parameters and data."""
        endpoint_url = f'{endpoint}?{parse.urlencode(query)}'
        headers = {
            'Content-Type': 'application/json',
        }
        # Add the bearer token if applicable
        if self.bearer_token:
            self.refresh_bearer_token()
            headers['authorization'] = f'Bearer {self.bearer_token}'

        response = request._execute_request(
            endpoint_url,
            'POST',
            headers=headers,
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

    def verify_age(self, video_id):
        """Make a request to the age_verify endpoint.

        Notable examples of the types of video this verification step is for:
        * https://www.youtube.com/watch?v=QLdAhwSBZ3w
        * https://www.youtube.com/watch?v=hc0ZDaAZQT0

        :param str video_id:
            The video id to get player info for.
        :rtype: dict
        :returns:
            Returns information that includes a URL for bypassing certain restrictions.
        """
        endpoint = f'{self.base_url}/verify_age'
        data = {
            'nextEndpoint': {
                'urlEndpoint': {
                    'url': f'/watch?v={video_id}'
                }
            },
            'setControvercy': True
        }
        data.update(self.base_data)
        result = self._call_api(endpoint, self.base_params, data)
        return result

    def get_transcript(self, video_id):
        """Make a request to the get_transcript endpoint.

        This is likely related to captioning for videos, but is currently untested.
        """
        endpoint = f'{self.base_url}/get_transcript'
        query = {
            'videoId': video_id,
        }
        query.update(self.base_params)
        result = self._call_api(endpoint, query, self.base_data)
        return result

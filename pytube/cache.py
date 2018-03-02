from functools import lru_cache

from pytube import request

@lru_cache(maxsize=None)
def get_js(js_url):
    return request.get(js_url)

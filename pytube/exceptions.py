class MultipleObjectsReturned(Exception):
    """
    The query returned multiple objects when only one was expected.
    """
    pass


class YouTubeError(Exception):
    """
    The REST interface returned an error.
    """
    pass

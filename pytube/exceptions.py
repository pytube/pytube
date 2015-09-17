class MultipleObjectsReturned(Exception):
    """The query returned multiple objects when only one was expected.
    """
    pass


class YouTubeError(Exception):
    """The REST interface returned an error.
    """
    pass


class CipherError(Exception):
    """The _cipher method returned an error.
    """
    pass


class DoesNotExist(Exception):
    """The requested video does not exist.
    """
    pass

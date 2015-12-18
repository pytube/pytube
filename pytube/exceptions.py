class MultipleObjectsReturned(Exception):
    """The query returned multiple objects when only one was expected.
    """
    pass


class ExtractorError(Exception):
    """Something specific to the js parser failed.
    """


class PytubeError(Exception):
    """Something specific to the wrapper failed.
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


class AgeRestricted(Exception):
    """The requested video has an age restriction.
    """
    pass

import re
from sys import stdout
from time import clock

def safe_filename(text, max_length=200):
    """
    Sanitizes filenames for many operating systems.

    Keyword arguments:
    text -- The unsanitized pending filename.
    """
    #Quickly truncates long filenames.
    truncate = lambda text: text[:max_length].rsplit(' ', 0)[0]

    #Tidy up ugly formatted filenames.
    text = text.replace('_', ' ')
    text = text.replace(':', ' -')

    #NTFS forbids filenames containing characters in range 0-31 (0x00-0x1F)
    ntfs = [chr(i) for i in range(0, 31)]

    #Removing these SHOULD make most filename safe for a wide range
    #of operating systems.
    paranoid = ['\"', '\#', '\$', '\%', '\'', '\*', '\,', '\.', '\/', '\:',
                '\;', '\<', '\>', '\?', '\\', '\^', '\|', '\~', '\\\\']

    blacklist = re.compile('|'.join(ntfs + paranoid), re.UNICODE)
    filename = blacklist.sub('', text)
    return truncate(filename)

def sizeof(bytes):
    """ Takes the size of file or folder in bytes and
        returns size formatted in kb, MB, GB, TB or PB.

        Args:
            bytes(int): size of the file in bytes
        Return:
            (str): containing size with formatting.
    """
    alternative = [
        (1024 ** 5, ' PB'),
        (1024 ** 4, ' TB'),
        (1024 ** 3, ' GB'),
        (1024 ** 2, ' MB'),
        (1024 ** 1, ' KB'),
        (1024 ** 0, (' byte', ' bytes')),
    ]

    for factor, suffix in alternative:
        if bytes >= factor:
            break
    amount = int(bytes/factor)
    if isinstance(suffix, tuple):
        singular, multiple = suffix
        if amount == 1:
            suffix = singular
        else:
            suffix = multiple
    return "%s%s" % (str(amount), suffix)


def print_status(progress, file_size, start):
    """
    This function - when passed as `on_progress` to `Video.download` - prints
    out the current download progress.

    Arguments:
    progress -- The lenght of the currently downloaded bytes.
    file_size -- The total size of the video.
    start -- time when started
    """
    done = int(50 * progress / int(file_size))
    percentDone = int(progress) * 100. / file_size
    speed = sizeof(progress//(clock() - start))
    bar = '=' * done
    die = ' ' * (50-done)
    stdout.write("\r[%s%s][%3.2f%%] %s of %s at %s/s   " % (bar, die, percentDone, sizeof(progress), sizeof(file_size), speed))
    stdout.flush()

from __future__ import unicode_literals
from os.path import normpath, isfile
from os import remove
from urllib2 import urlopen
from sys import exit


class Video(object):
    """
    Class representation of a single instance of a YouTube video.

    """
    def __init__(self, url, filename, **attributes):
        """
        Define the variables required to declare a new video.

        Keyword arguments:
        extention -- The file extention the video should be saved as.
        resolution -- The broadcasting standard of the video.
        url -- The url of the video. (e.g.: youtube.com/watch?v=..)
        filename -- The filename (minus the extention) to save the video.
        """

        self.url = url
        self.filename = filename
        self.__dict__.update(**attributes)

    def download(self, path=None, chunk_size=8*1024,
                 on_progress=None, on_finish=None):
        """
        Downloads the file of the URL defined within the class
        instance.

        Keyword arguments:
        path -- Destination directory
        chunk_size -- File size (in bytes) to write to buffer at a time
                      (default: 8 bytes).
        on_progress -- A function to be called every time the buffer was
                       written out. Arguments passed are the current and
                       the full size.
        on_finish -- To be called when the download is finished. The full
                     path to the file is passed as an argument.

        """

        path = (normpath(path) + '/' if path else '')
        fullpath = '{0}{1}.{2}'.format(path, self.filename, self.extension)

	# Check for conflicting filenames
	if isfile(fullpath):
		print "\n\nError: Conflicting filename: '{}'.\n\n".format(self.filename)
		exit(1)

        response = urlopen(self.url)
        meta_data = dict(response.info().items())
        file_size = int(meta_data.get("Content-Length") or
                         meta_data.get("content-length"))
        self._bytes_received = 0
	try:
        	with open(fullpath, 'wb') as dst_file:
        # Print downloading message
       	    		print "\nDownloading: '{0}.{1}' (Bytes: {2})\n\n".format(self.filename, self.extension, file_size)

            		while True:
                		self._buffer = response.read(chunk_size)
                		if not self._buffer:
                    			if on_finish:
                        			on_finish(fullpath)
                    			break

                		self._bytes_received += len(self._buffer)
                		dst_file.write(self._buffer)
                		if on_progress:
                    			on_progress(self._bytes_received, file_size)

	# Catch possible exceptions occurring during download
	except IOError:
		print """\n\nError: Failed to open file.\nCheck that: ('{0}'), is a valid pathname.
			 	\nOr that ('{1}.{2}') is a valid filename.\n\n""".format(path, self.filename, self.extension)
		exit(2)

	except BufferError:
		print "\n\nError: Failed on writing buffer.\nFailed to write video to file.\n\n"
		exit(1)

	except KeyboardInterrupt:
		print "\n\nInterrupt signal given.\nDeleting incomplete video ('{0}.{1}').\n\n".format(self.filename, self.extension)
		remove(fullpath)
		exit(1)


    def __repr__(self):
        """A cleaner representation of the class instance."""
        return "<Video: {0} (.{1}) - {2}>".format(self.video_codec, self.extension,
                                           self.resolution)

    def __lt__(self, other):
        if type(other) == Video:
            v1 = "{0} {1}".format(self.extension, self.resolution)
            v2 = "{0} {1}".format(other.extension, other.resolution)
            return (v1 > v2) - (v1 < v2) < 0

.. pytube documentation master file, created by sphinx-quickstart on Mon Oct  9 02:11:41 2017.

pytube
======
Release v\ |version|. (:ref:`Installation<install>`)

.. image:: https://img.shields.io/pypi/v/pytube.svg
  :alt: Pypi
  :target: https://pypi.python.org/pypi/pytube/

.. image:: https://img.shields.io/pypi/pyversions/pytube.svg
  :alt: Python Versions
  :target: https://pypi.python.org/pypi/pytube/

.. image:: https://readthedocs.org/projects/python-pytube/badge/?version=latest&style=flat-square
  :alt: Readthedocs

**pytube** is a lightweight, Pythonic, dependency-free, library (and
command-line utility) for downloading YouTube Videos.

-------------------

**Behold, a perfect balance of simplicity versus flexibility**::

    >>> from pytube import YouTube
    >>> YouTube('https://youtu.be/9bZkp7q19f0').streams.first().download()
    >>> yt = YouTube('http://youtube.com/watch?v=9bZkp7q19f0')
    >>> yt.streams
    ... .filter(progressive=True, file_extension='mp4')
    ... .order_by('resolution')
    ... .desc()
    ... .first()
    ... .download()

Features
--------

- Support for Both Progressive & DASH Streams
- Easily Register ``on_download_progress`` & ``on_download_complete`` callbacks
- Command-line Interfaced Included
- Caption Track Support
- Outputs Caption Tracks to .srt format (SubRip Subtitle)
- Ability to Capture Thumbnail URL.
- Extensively Documented Source Code
- No Third-Party Dependencies

The User Guide
--------------
This part of the documentation begins with some background information about
the project, then focuses on step-by-step instructions for getting the most out
of pytube.

.. toctree::
   :maxdepth: 2

   user/install
   user/quickstart
   user/streams
   user/captions
   user/playlist
   user/channel
   user/search
   user/cli
   user/exceptions

The API Documentation
-----------------------------

If you are looking for information on a specific function, class, or method,
this part of the documentation is for you.

.. toctree::
   :maxdepth: 2

   api


Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

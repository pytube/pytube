.. pytube documentation master file, created by
   sphinx-quickstart on Mon Oct  9 02:11:41 2017.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

pytube
======
Release v\ |version|. (:ref:`Installation <install>`)

.. image:: https://img.shields.io/pypi/v/pytube.svg
  :alt: Pypi
  :target: https://pypi.python.org/pypi/pytube/

.. image:: https://travis-ci.org/nficano/pytube.svg?branch=master
   :alt: Build status
   :target: https://travis-ci.org/nficano/pytube

.. image:: https://readthedocs.org/projects/python-pytube/badge/?version=latest
  :target: http://python-pytube.readthedocs.io/en/latest/?badge=latest
  :alt: Documentation Status

.. image:: https://coveralls.io/repos/github/nficano/pytube/badge.svg?branch=master
  :alt: Coverage
  :target: https://coveralls.io/github/nficano/pytube?branch=master

**pytube** is a lightweight, Pythonic, dependency-free, library (and command-line utility) for downloading YouTube Videos.

-------------------

**Behold, a perfect balance of simplicity versus flexibility**::

    >>> YouTube('http://youtube.com/watch?v=9bZkp7q19f0').streams.first().download()
    >>> yt = YouTube('http://youtube.com/watch?v=9bZkp7q19f0')
    >>> yt.streams
    ... .filter(progressive=True, subtype='mp4')
    ... .order_by('resolution')
    ... .desc()
    ... .first()
    ... .download()

The User Guide
--------------
This part of the documentation begins with some background information about the project, then focuses on step-by-step instructions for getting the most out of pytube.

The API Documentation / Guide
-----------------------------

If you are looking for information on a specific function, class, or method, this part of the documentation is for you.

.. toctree::
   :maxdepth: 2

   api


Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

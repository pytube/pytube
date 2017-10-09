======
pytube
======

.. image:: https://img.shields.io/pypi/v/pytube.svg
  :alt: Pypi
  :target: https://pypi.python.org/pypi/pytube/

.. image:: https://travis-ci.org/nficano/pytube.svg?branch=master
   :alt: Build status
   :target: https://travis-ci.org/nficano/pytube

.. image:: https://coveralls.io/repos/nficano/pytube/badge.svg?branch=master&service=github
  :alt: Coverage
  :target: https://coveralls.io/github/nficano/pytube?branch=master

*pytube* is a lightweight, dependency-free Python library (and command-line utility) for downloading YouTube Videos.

Description
===========

YouTube is the most popular video-sharing platform in the world and as a hacker you may encounter a situation where you want to script something to download videos.  For this I present to you *pytube*.

*pytube* is a lightweight library written in Python. It has no third party dependencies and aims to be highly reliable.

*pytube* makes *zero assumptions*, meaning there is no built-in method to get say the *"best"* quality video, *pytube* simply exposes all the available formats and resolutions, giving you the developer the power to define what *"best"* is.

*pytube* also makes pipelining easy, allowing you to specify callback functions for different download events, such as  ``on progress`` or ``on complete``.

Finally *pytube* also includes a command-line utility, allowing you to quickly download videos right from terminal.

Installation
============

Download using pip via pypi.

.. code:: bash

    pip install pytube

Easy as Pie 💥
==============

Behold, the power of pytube:

.. code-block:: python

   >>> from pytube import YouTube
   >>> YouTube('http://youtube.com/watch?v=9bZkp7q19f0').streams.first().download()

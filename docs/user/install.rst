.. _install:

Installation of pytube
======================

This guide assumes you already have python and pip installed.

To install pytube, run the following command in your terminal::

    $ pip install pytube

Get the Source Code
-------------------

pytube is actively developed on GitHub, where the source is `available <https://github.com/sluggish-yard/pytube-saguaro>`_.

You can either clone the public repository::

    $ git clone https://github.com/sluggish-yard/pytube-saguaro.git

Or, download the `tarball <https://github.com/sluggish-yard/pytube-saguaro/tarball/master>`_::

    $ curl -OL https://github.com/sluggish-yard/pytube-saguaro/tarball/master
    # optionally, zipball is also available (for Windows users).

Once you have a copy of the source, you can embed it in your Python package, or install it into your site-packages by running::

    $ cd pytube
    $ python -m pip install .

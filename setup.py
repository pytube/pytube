#!/usr/bin/env python
# -*- coding: utf-8 -*-

from pytube import __version__
import os


try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup


def open_file(fname):
    return open(os.path.join(os.path.dirname(__file__), fname))


setup(
    name="pytube",
    version=__version__,
    author="Nick Ficano",
    author_email="nficano@gmail.com",
    packages=['pytube'],
    url="http://pytube.nickficano.com",
    license=open_file('LICENSE.txt').read(),
    scripts=['scripts/pytube'],
    classifiers=[
        "Development Status :: 4 - Beta",
        "Environment :: Console",
        "Intended Audience :: Developers",
        "Programming Language :: Python",
        "Natural Language :: English",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 2.6",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3.0",
        "Programming Language :: Python :: 3.4",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Utilities",
        "Topic :: Internet",
        "Topic :: Multimedia :: Video"
    ],
    description="A simple, yet versatile package for downloading "
                "YouTube videos.",
    long_description=open_file('README.rst').read(),
    zip_safe=True,
)

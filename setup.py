#!/usr/bin/env python
# -*- coding: utf-8 -*-
from pytube import __version__

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

with open('README.rst') as readme_file:
    readme = readme_file.read()

with open('LICENSE.txt') as readme_file:
    license = readme_file.read()

setup(
    name="pytube",
    version=__version__,
    author="Nick Ficano",
    author_email="nficano@gmail.com",
    packages=['pytube'],
    url="https://github.com/nficano/pytube",
    license=license,
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
        "Programming Language :: Python :: 3.2",
        "Programming Language :: Python :: 3.3",
        "Programming Language :: Python :: 3.4",
        "Programming Language :: Python :: 3.5",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Utilities",
        "Topic :: Internet",
        "Topic :: Multimedia :: Video"
    ],
    description=("A simple, yet versatile Python library (and command-line) "
                 "for downloading YouTube videos."),
    long_description=readme,
    zip_safe=True,
)

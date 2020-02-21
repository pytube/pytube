#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""This module contains setup instructions for pytube3."""
import codecs
import os
from setuptools import setup

here = os.path.abspath(os.path.dirname(__file__))

with codecs.open(os.path.join(here, "README.md"), encoding="utf-8") as fh:
    long_description = "\n" + fh.read()

with open(os.path.join(here, "pytube", "version.py")) as fp:
    exec(fp.read())

setup(
    name="pytube3",
    version=__version__,  # noqa: F821
    author="Nick Ficano, Harold Martin",
    author_email="nficano@gmail.com, harold.martin@gmail.com",
    packages=["pytube", "pytube.contrib"],
    package_data={"": ["LICENSE"],},
    url="https://github.com/hbmartin/pytube3",
    license="MIT",
    entry_points={"console_scripts": ["pytube3 = pytube.cli:main",],},
    install_requires=["typing_extensions"],
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Environment :: Console",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Natural Language :: English",
        "Operating System :: MacOS",
        "Operating System :: Microsoft",
        "Operating System :: POSIX",
        "Operating System :: Unix",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python",
        "Topic :: Internet",
        "Topic :: Multimedia :: Video",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Terminals",
        "Topic :: Utilities",
    ],
    description=("Python 3 library for downloading YouTube Videos."),
    include_package_data=True,
    long_description_content_type="text/markdown",
    long_description=long_description,
    zip_safe=True,
    python_requires=">=3.6",
    project_urls={
        "Bug Reports": "https://github.com/hbmartin/pytube3/issues",
        "Read the Docs": "https://pytube3.readthedocs.io/en/latest/?badge=latest",
    },
    keywords=["youtube", "download", "video", "stream",],
)

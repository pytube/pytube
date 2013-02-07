#!/usr/bin/env python

from distutils.core import setup
import pytube

packages = [
    'pytube'
]

setup(
    name="pytube",
    version=pytube.__version__,
    description="A simple, yet versatile package for downloading " \
                "YouTube videos.",
    author="Nick Ficano",
    author_email="nficano@gmail.com",
    url="http://pytube.nickficano.com",
    packages=packages,
    download_url="https://github.com/NFicano/pytube/tarball/0.1.16",
    license="MIT License",
    scripts = ['pytube/bin/pytube.py'],
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
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Utilities",
        "Topic :: Internet",
        "Topic :: Multimedia :: Video"
    ],
)

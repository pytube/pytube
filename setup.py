import os
from setuptools import setup

"""
PyTube
-------
"""


def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

setup(
    name="pytube",
    version="0.0.5",
    author="Nick Ficano",
    author_email="nficano@gmail.com",
    description="A simple, yet versatile package for downloading YouTube videos.",
    license='The MIT License: http://www.opensource.org/licenses/mit-license.php',
    keywords="youtube downloader",
    url="https://github.com/NFicano/python-youtube-download",
    download_url="https://github.com/NFicano/python-youtube-download/tarball/master",
    packages=['pytube'],
    use_2to3=True,
    long_description=read('README.md'),
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
    ],
)

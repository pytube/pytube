import os
from setuptools import setup

"""
PyTube
-------
"""

def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

setup(
    name = "pytube",
    version = "0.0.4",
    author = "Nick Ficano",
    author_email = "nficano@gmail.com",
    description = "A lightwight, dependency-free YouTube Video downloading library",
    license='The MIT License: http://www.opensource.org/licenses/mit-license.php',
    keywords = "youtube downloader",
    url = "https://github.com/NFicano/python-youtube-download",
    download_url="https://github.com/NFicano/python-youtube-download/tarball/master",
    packages=['pytube'],
    long_description=read('README.md'),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Environment :: Console",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 2.6",
        "Programming Language :: Python :: 2.7",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Utilities",
    ],
)

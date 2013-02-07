#!/usr/bin/env python

import os
from setuptools import setup

packages = [
    'pytube'
]

requires = []


def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

setup(
    name="pytube",
    version="0.1.12",
    description="",
    author="Nick Ficano",
    author_email="nficano@gmail.com",
    url="http://pytube.nickficao.com",
    packages=packages,
    package_data={'': ['LICENSE']},
    package_dir={'pytube': 'pytube'},
    download_url="https://github.com/NFicano/pytube/tarball/0.1.12",
    include_package_data=True,
    install_requires=requires,
    license=open("LICENSE").read(),

    use_2to3=True,
    entry_points={
        "console_scripts": [
            "pytube=pytube:_main",
        ]},
    long_description=open('README.md').read(),
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

# -*- coding: utf-8 -*-
from pytube import Playlist


def test_construct():
    ob = Playlist(
        'https://www.youtube.com/watch?v=m5q2GCsteQs&list='
        'PL525f8ds9RvsXDl44X6Wwh9t3fCzFNApw',
    )
    expected = 'https://www.youtube.com/' \
               'playlist?list=' \
               'PL525f8ds9RvsXDl44X6Wwh9t3fCzFNApw'

    assert ob.construct_playlist_url() == expected


def test_link_parse():
    ob = Playlist(
        'https://www.youtube.com/watch?v=m5q2GCsteQs&list='
        'PL525f8ds9RvsXDl44X6Wwh9t3fCzFNApw',
    )

    expected = [
        '/watch?v=m5q2GCsteQs',
        '/watch?v=5YK63cXyJ2Q',
        '/watch?v=Rzt4rUPFYD4',
    ]
    assert ob.parse_links() == expected


def test_populate():
    ob = Playlist(
        'https://www.youtube.com/watch?v=m5q2GCsteQs&list='
        'PL525f8ds9RvsXDl44X6Wwh9t3fCzFNApw',
    )
    expected = [
        'https://www.youtube.com/watch?v=m5q2GCsteQs',
        'https://www.youtube.com/watch?v=5YK63cXyJ2Q',
        'https://www.youtube.com/watch?v=Rzt4rUPFYD4',
    ]

    ob.populate_video_urls()
    assert ob.video_urls == expected


def test_download():
    ob = Playlist(
        'https://www.youtube.com/watch?v=lByG_AgKS9k&list='
        'PL525f8ds9RvuerPZ3bZygmNiYw2sP4BDk',
    )
    ob.download_all()

# -*- coding: utf-8 -*-
from pytube import Playlist

short_test_pl = 'https://www.youtube.com/watch?v=' \
    'm5q2GCsteQs&list=PL525f8ds9RvsXDl44X6Wwh9t3fCzFNApw'
long_test_pl = 'https://www.youtube.com/watch?v=' \
               '9CHDoAsX1yo&list=UUXuqSBlHAE6Xw-yeJA0Tunw'


def test_construct():
    ob = Playlist(short_test_pl)
    expected = 'https://www.youtube.com/' \
               'playlist?list=' \
               'PL525f8ds9RvsXDl44X6Wwh9t3fCzFNApw'

    assert ob.construct_playlist_url() == expected


def test_populate():
    ob = Playlist(short_test_pl)
    expected = [
        'https://www.youtube.com/watch?v=m5q2GCsteQs',
        'https://www.youtube.com/watch?v=5YK63cXyJ2Q',
        'https://www.youtube.com/watch?v=Rzt4rUPFYD4',
    ]

    ob.populate_video_urls()
    assert ob.video_urls == expected


def test_link_parse():
    ob = Playlist(short_test_pl)

    expected = [
        '/watch?v=m5q2GCsteQs',
        '/watch?v=5YK63cXyJ2Q',
        '/watch?v=Rzt4rUPFYD4',
    ]
    assert ob.parse_links() == expected


def test_download():
    ob = Playlist(short_test_pl)
    ob.download_all()
    ob.download_all('.')
    ob.download_all(prefix_number=False)
    ob.download_all('.', prefix_number=False)


def test_numbering():
    ob = Playlist(short_test_pl)
    ob.populate_video_urls()
    gen = ob._path_num_prefix_generator(reverse=False)
    assert '1' in next(gen)
    assert '2' in next(gen)

    ob = Playlist(short_test_pl)
    ob.populate_video_urls()
    gen = ob._path_num_prefix_generator(reverse=True)
    assert str(len(ob.video_urls)) in next(gen)
    assert str(len(ob.video_urls) - 1) in next(gen)

    ob = Playlist(long_test_pl)
    ob.populate_video_urls()
    gen = ob._path_num_prefix_generator(reverse=False)
    nxt = next(gen)
    assert len(nxt) > 1
    assert '1' in nxt
    nxt = next(gen)
    assert len(nxt) > 1
    assert '2' in nxt

    ob = Playlist(long_test_pl)
    ob.populate_video_urls()
    gen = ob._path_num_prefix_generator(reverse=True)
    assert str(len(ob.video_urls)) in next(gen)
    assert str(len(ob.video_urls) - 1) in next(gen)

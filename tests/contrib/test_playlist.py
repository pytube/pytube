from pytube import Playlist


def test_title():
    url = "https://www.youtube.com/playlist?list=PLsyeobzWxl7poL9JTVyndKe62ieoN-MZ3"
    pl = Playlist(url)
    pl_title = pl.title()
    assert pl_title == "Python Tutorial for Beginners"

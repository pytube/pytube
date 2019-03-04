from pytube import YouTube, Playlist

def test_title():
	pl = Playlist("https://www.youtube.com/watch?v=QXeEoD0pB3E&list=PLsyeobzWxl7poL9JTVyndKe62ieoN-MZ3")
	pl_title = pl.title()
	assert pl_title == "Python Tutorial for Beginners"
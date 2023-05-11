from tempfile import TemporaryDirectory
from time import time

from pytube import YouTube


def test_video_stream_1080p():
    video = YouTube('https://www.youtube.com/watch?v=2lAe1cqCOXo')

    stream = video.streams.filter(only_video=True, resolution='1080p').first()
    stream_size = stream.filesize

    before = time()
    with TemporaryDirectory() as tmp_dir:
        stream.download(output_path=tmp_dir, filename='stream')
    after = time()

    assert stream_size / (after - before) > 5 * 1024 * 1024  # 5 MB/s

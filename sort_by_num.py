from pytube import YouTube

yt = YouTube('https://www.youtube.com/watch?v=5cvM-crlDvg')
print(yt.streams.filter(only_audio=True).order_by('abr').all())
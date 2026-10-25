from pytubefix import YouTube
from pytubefix.cli import on_progress

url1 = "https://youtu.be/MkBulXQ444o?si=wrY6shZ3JJDF8P4O"
url2 = "https://youtu.be/k-3PoOT4vOM?si=PM9yFn7lwGaICYTi"

yt = YouTube(url2, on_progress_callback=on_progress)
print(yt.title)

ys = yt.streams.get_highest_resolution()
ys.download()
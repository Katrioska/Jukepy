from pytube import YouTube
from os import path
from os import remove
from moviepy.editor import *
import sys

def YouTubeMP3Downloader(videoURL, output=False):
    videoURL = "https://www.youtube.com/watch?v=vWltUi1zXWM"
    if output: print(f"[*] Video URL is: {videoURL}")
    yt = YouTube(videoURL)
    music = yt.streams.filter(progressive=True).first()
    if output: print(f"[*] Video Title is: {music.title}")

    if output: print("[*] Downloading Video...")
    try:
        music.download()
    except(AttributeError):
        print("[!] Video is cannot downloaded. (Try later)")
        return None
    if output: print("[*] Done.")


    if (path.exists(music.title+".mp4")):
        if output: print("[*] Video format is mp4. Changing to mp3...")
        video = VideoFileClip(path.join(music.title+".mp4"))
        video.audio.write_audiofile(path.join(music.title+".mp3"))
        video.close()
        remove(music.title + ".mp4")
        if output: print("[*] Done")
        return music.title+".mp3"

    elif (path.exists(music.title+".mp3")):
        if output: print("[*] Video format is mp3. Done.")
        return music.title+".mp3"
    else:
        if output: print("[!] Format unknown.")
        return None

if __name__ == "__main__":
    YouTubeMP3Downloader(sys.argv[-1], output=True)
from pytube import YouTube
from os import path, remove
from moviepy.editor import *
from shutil import move
import logging
import sys

def YouTubeMP3Downloader(videoURL, logger = None, path_to_download=""):
    yt = YouTube(videoURL)
    music = yt.streams.filter(progressive=True).first()
    if logger != None: logger.debug(f"Video title is {music.title}")

    if logger != None: logger.debug("Downloading Video...")
    try:
        music.download()
    except(AttributeError):
        logger.error("Video is cannot downloaded. (Try later)")
        return None
    if logger != None: logger.debug("Video downloaded successful")

    title = music.title.replace('"', "")

    if (path.exists(title+".mp4")):
        if logger != None: logger.debug("Video format is mp4. Changing to mp3...")
        video = VideoFileClip(path.join(title+".mp4"))
        video.audio.write_audiofile(path.join(title+".mp3"))
        video.close()
        remove(title + ".mp4")
        if logger != None: logger.debug("Conversion done")

        if path_to_download != "":
            move(title+".mp3", path_to_download+"\\"+title+".mp3")
        return title+".mp3"

    elif (path.exists(title+".mp3")):
        if logger != None: logger.debug("Video format is mp3. Done.")
        return music.title+".mp3"
    else:
        if logger != None: logger.error("Format unknown.")
        return None

if __name__ == "__main__":
    YouTubeMP3Downloader(sys.argv[-1])
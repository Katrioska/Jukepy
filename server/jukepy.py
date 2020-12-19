import socket
import threading
import logging
from sys import stdout, exit
from os import mkdir, listdir, remove, path
from datetime import datetime
from pickle import loads, dumps
from pygame import mixer

from ytmp3_downloader import YouTubeMP3Downloader

mixer.init()

class ClientDisconnected(Exception):
    pass

class Jukepy:
    def __init__(self, address):
        self.__server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.__server.bind(address)

        self.__rootLogger = logging.getLogger()

        self.__formatter = logging.Formatter("%(asctime)s [%(threadName)-12.12s] [%(levelname)-5.5s]  %(message)s")

        self.__console_handler = logging.StreamHandler(stdout)
        self.__console_handler.setLevel(logging.DEBUG)
        self.__console_handler.setFormatter(self.__formatter)

        self.__filename='Logs\\%s_server.log' % datetime.now().strftime('%Y-%m-%d=%H%M%S')
        try:
            self.__file_handler = logging.FileHandler(filename=self.__filename)
        except FileNotFoundError:
            mkdir("Logs")
            self.__file_handler = logging.FileHandler(filename=self.__filename)

        self.__file_handler.setFormatter(self.__formatter)
        self.__file_handler.setLevel(logging.DEBUG)

        self.__rootLogger.addHandler(self.__file_handler)
        self.__rootLogger.addHandler(self.__console_handler)
        self.__rootLogger.setLevel(logging.DEBUG)
        self.__rootLogger.debug("Logging handlers and server created succesful.")

        self.__quehue = []
        self.__isPlaying = False

        self.__toSend = None

        self.__running = True

    def run(self):
        threadServer = threading.Thread(target=self.serverThread)
        threadServer.daemon = True
        self.__rootLogger.debug("Starting server thread.")
        threadServer.start()
        self.__rootLogger.info("[*] Use 'CTRL + C' to stop the server" )
        try:
            while self.__running:
                continue
        except(KeyboardInterrupt):
            self.__rootLogger.info("Keyboard Interrupt (Contol + C) detected. Closing Threads...")
            self.__close()

    def __close(self):
        self.__running = False
        self.__server.close()

    def serverThread(self):
        self.__server.listen(10)
        self.__rootLogger.info("Waiting for connections.")
        while self.__running:
            client, address = self.__server.accept()
            #client.settimeout(60)
            self.__rootLogger.info(f"Attempt to client connection in {address}.")
            threadClient = threading.Thread(target=self.clientThread, args=(client, address))
            threadClient.daemon = True
            self.__rootLogger.debug("Starting client thread.")
            threadClient.start()

    def clientThread(self, client, address):
        self.__rootLogger.debug("Client thread created succesful.")
        while True:
            try:
                data = client.recv(1024)
                if data:
                    loadedData = loads(data)
                    if(loadedData["justplay"]):
                        self.__JustPlay(loadedData["link"], destroy=loadedData["destroy"])

                if self.__toSend != None:
                    client.send(self.__toSend)
                    self.__toSend = None

                if not self.__running:
                    self.__rootLogger.info("Closing client thread")
                    client.close()
                    return False

            except ClientDisconnected:
                self.__rootLogger.info(f"Client in {address} disconnected.")

            except Exception as error:
                self.__rootLogger.error("Error in client handler: ", exc_info=True)
                client.close()
                self.__rootLogger.info(f"Client in {address} disconnected.")
                return False

    def __JustPlay(self, music_link, destroy = False):
        tosend = {"status" : "",
                  "continue" : False}

        try:
            mkdir("tempmusic")
        except(FileExistsError):
            pass

        self.__rootLogger.debug(f"Music link is: {music_link}")
        self.__rootLogger.debug("Starting mp3 download.")

        tosend["status"] = f"Music link is: {music_link}. Starting mp3 download."
        self.__toSend = tosend

        music_name = YouTubeMP3Downloader(music_link, path_to_download="tempmusic", logger=self.__rootLogger)

        if music_name == None:
            self.__rootLogger.error("No music returned from YouTube MP3 downloader function.")
            tosend["status"] = "No music returned from YouTube MP3 downloader function."
            self.__toSend = tosend
            return False

        if not self.__isPlaying:
            tosend["status"] = f"Playing {music_name}."
            self.__toSend = tosend

            music = mixer.Sound(f"tempmusic\\{music_name}")
            channel = mixer.Channel(0)
            self.__rootLogger.info(f"Playing '{music_name}.'")
            channel.play(music)

            while True:
                self.__isPlaying = True
                if not mixer.Channel(0).get_busy():
                    self.__rootLogger.info(f"'{music_name} finished.")
                    self.__isPlaying = False
                    tosend["status"] = "Music finished"
                    tosend["continue"] = True
                    self.__toSend = tosend
                    break

            if destroy:
                remove(path.join("tempmusic", music_name))

            return True

        else:
            return False



    def deleteLogs(self):
        logs = listdir("Logs")

        for file in logs:
            if file.endswith(".log"):
                remove(path.join("Logs", file))
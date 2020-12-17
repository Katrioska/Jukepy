import socket
import logging
from sys import stdout, exit
from datetime import datetime
from os import mkdir
from pickle import dumps, loads

class JukepyClient:
    def __init__(self):
        self.__client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

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
        self.__rootLogger.debug("Logging handlers and client created succesful.")

        self.__justplay = None

    def connect(self, server_ip, port):
        try:
            self.__client.connect((server_ip, port))
            self.__rootLogger.info(f"Connected to server in {server_ip, port}.")
        except Exception as error:
            self.__rootLogger.error(f"Cannot connect to server in {server_ip, port}.",exc_info=True)

    def isJustPlay(self, boolean):
        self.__justplay = boolean
        self.__rootLogger.debug(f"Justplay value set to {boolean}")

    def sendYTlink(self, link):
        tosend = {"justplay" : self.__justplay,
                  "link" : link}
        try:
            self.__client.send(dumps(tosend))
            self.__rootLogger.info("Data sended")
        except Exception as error:
            self.__rootLogger.error(f"Error sending dumped data to server. ", exc_info=True)
            return False

        self.__rootLogger.debug("Waiting for server response...")
        while True:
            data = self.__client.recv(1024)
            if data:
                break

        if loads(data):
            self.__rootLogger.info("YT link can be played")
            return True
        else:
            self.__rootLogger.info("YT link cannot be played")
            return False
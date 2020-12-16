import socket
import threading
import logging
from sys import stdout
from os import mkdir
from datetime import datetime

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

        self.__running = True
        self.__buffersize = 1024

    def run(self):
        threadServer = threading.Thread(target=self.serverThread)
        threadServer.daemon = True
        threadServer.start()
        self.__rootLogger.debug("Starting server thread.")

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
            client.settimeout(60)
            self.__rootLogger.info(f"Attempt to client connection in {address}.")
            threadClient = threading.Thread(target=self.clientThread, args=(client, address))
            threadClient.daemon = True
            self.__rootLogger.debug("Starting client thread.")
            threadClient.start()

    def clientThread(self, client, address):
        self.__rootLogger.debug("Client thread created succesful.")
        while True:
            try:
                data = client.recv(self.__buffersize)
                if data:
                    print(data.decode())
                    if (data.decode()=="close"):
                        raise ClientDisconnected("Client send 'close' command")
                else:
                    print("no data recived")

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

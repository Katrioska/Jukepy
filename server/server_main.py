from jukepy import Jukepy

if __name__ == "__main__":
    server = Jukepy(('localhost', 2525))
    server.run()
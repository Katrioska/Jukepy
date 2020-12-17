from jukepy_client import JukepyClient

def main():
    client = JukepyClient()
    client.connect('localhost', 2525)
    client.isJustPlay(True)

    while True:
        link = input("#: ")
        if link == "close":
            break
        else:
            client.sendYTlink(link)

if __name__ == "__main__":
    main()
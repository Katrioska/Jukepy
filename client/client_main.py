import socket

def main():
    host = 'localhost'
    port = 2525

    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((host, port))
    while True:
        tosend = input("#: ")
        s.send(tosend.encode())
        if tosend == "close":
            break

    s.close()

if __name__ == "__main__":
    main()
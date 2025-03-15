import time

from pythonosc import udp_client

ip = "127.0.0.1"
port = 8085
client = udp_client.SimpleUDPClient(ip, port)


def main():
    client.send_message("/projection", [0.5])


if __name__ == "__main__":
    main()

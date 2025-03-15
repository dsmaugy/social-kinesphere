import time

from pythonosc import udp_client

ip = "192.168.0.194"
port = 8085
client = udp_client.SimpleUDPClient(ip, port)


def main():
    client.send_message("/mix", [0.1])


if __name__ == "__main__":
    main()

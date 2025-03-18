import sys
import time

from pythonosc import udp_client

ip = "127.0.0.1"
port = 8085
client = udp_client.SimpleUDPClient(ip, port)


def main():
    client.send_message("/mix", [float(sys.argv[1])])


if __name__ == "__main__":
    main()

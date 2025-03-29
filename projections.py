import math
import os
import socket
import threading
import tkinter as tk

import cv2
from PIL import Image, ImageTk
from pythonosc import dispatcher, osc_server

MAX_FRAME_DELAY = 1000
MIN_FRAME_DELAY = 10
OSC_PORT = 8085

host = socket.gethostname()

if not host.startswith("void"):
    host = "void2"

if host == "void1":
    video = cv2.VideoCapture("videos/void1.1.mp4")
    video2 = cv2.VideoCapture("videos/void1.2.mp4")
    defaultVideo = cv2.VideoCapture("videos/void1-default.mp4")
elif host == "void2":
    video = cv2.VideoCapture("videos/void2.1.mp4")
    video2 = cv2.VideoCapture("videos/void2.2.mp4")
    defaultVideo = cv2.VideoCapture("videos/void2-default.mp4")
elif host == "void3":
    video = cv2.VideoCapture("videos/void3.mp4")
    video2 = cv2.VideoCapture("videos/void3.mp4")
    defaultVideo = cv2.VideoCapture("videos/void3-default.mp4")
elif host == "void4":
    video = cv2.VideoCapture("videos/void4.mp4")
    video2 = cv2.VideoCapture("videos/void4.mp4")
    defaultVideo = cv2.VideoCapture("videos/void4-default.mp4")
else:
    print("Hostname not correct")
    exit(-1)

if video.isOpened() and video2.isOpened():
    print("Video Succefully opened")
else:
    print("Something went wrong check if the video name and path is correct")

if host == "void1" or host == "void2":
    BLENDING_ACTIVE = True
else:
    BLENDING_ACTIVE = False

root = tk.Tk()
root.title("Projections")
tk_frame = tk.IntVar(value=0)

label = tk.Label(root)
label.pack()

projection_width = 800
frame_delay = 100
video_mix = 0.0


def get_next_video_frame(mix=1.0):
    global video, video2, defaultVideo, BLENDING_ACTIVE

    if mix == 0.0:
        ret, frame = defaultVideo.read()
        if not ret:
            defaultVideo.set(cv2.CAP_PROP_POS_FRAMES, 0)
            _, frame = defaultVideo.read()
    else:
        ret, frame = video.read()
        if not ret:
            video.set(cv2.CAP_PROP_POS_FRAMES, 0)
            _, frame = video.read()

        if BLENDING_ACTIVE:
            ret, frame2 = video2.read()
            if not ret:
                video2.set(cv2.CAP_PROP_POS_FRAMES, 0)
                _, frame2 = video2.read()

            frame = cv2.addWeighted(frame, mix, frame2, 1.0 - mix, 0)

    return frame


def zoom_and_crop(frame, target_width, target_height):
    h, w, _ = frame.shape

    scale = target_height / h
    new_w, new_h = int(w * scale), target_height

    resized_frame = cv2.resize(frame, (new_w, new_h), interpolation=cv2.INTER_LINEAR)

    x_offset = max(0, (new_w - target_width) // 2)
    cropped_frame = resized_frame[:, x_offset : x_offset + target_width]

    return cropped_frame


def update_frame():
    global label, frame_delay, tk_frame
    frame_num = tk_frame.get()

    variable_mix = video_mix
    if BLENDING_ACTIVE:
        variable_mix = min(max(0.25 * (math.sin(frame_num * 0.085) + 1), 0.0), 0.5)

    frame = cv2.cvtColor(get_next_video_frame(variable_mix), cv2.COLOR_BGR2RGB)
    frame = zoom_and_crop(
        frame, root.winfo_screenheight() // 2, root.winfo_screenheight()
    )

    img = Image.fromarray(frame)
    imgtk = ImageTk.PhotoImage(image=img)

    label.imgtk = imgtk
    label.config(image=imgtk)

    tk_frame.set(frame_num + 1)
    root.after(frame_delay, update_frame)


def increase_width():
    global projection_width
    projection_width = min(projection_width + 10, root.winfo_screenwidth())


def decrease_width():
    global projection_width
    projection_width = max(projection_width - 10, 0)


def increase_speed():
    global frame_delay
    frame_delay = max(frame_delay - 10, MIN_FRAME_DELAY)


def decrease_speed():
    global frame_delay
    frame_delay = min(frame_delay + 10, MAX_FRAME_DELAY)


def decrease_mix():
    global video_mix
    video_mix = max(video_mix - 0.05, 0)


def increase_mix():
    global video_mix
    video_mix = min(video_mix + 0.05, 1.0)


def handle_osc(address, *args):
    print(f"osc msg: {address} {args}")
    if address == "/quit":
        root.destroy()
    elif address == "/mix":
        if len(args) > 0:
            try:
                global video_mix
                video_mix = max(min(float(args[0]), 1.0), 0.0)
                print(f"video mix: {video_mix}")
            except ValueError:
                print(f"ERROR: Cannot convert {args[0]} to float")
                pass


def run_osc():
    disp = dispatcher.Dispatcher()
    disp.map("/*", handle_osc)

    server = osc_server.ThreadingOSCUDPServer(("0.0.0.0", OSC_PORT), disp)
    print(f"OSC Server running on port {OSC_PORT}...")
    server.serve_forever()


def debug_terminal():
    while True:
        cmd = input("control: ")
        if cmd == "o":
            decrease_mix()
            print(f"mix: {video_mix}")
        elif cmd == "p":
            increase_mix()
            print(f"mix: {video_mix}")
        elif cmd == "k":
            decrease_speed()
            print(f"frame delay: {frame_delay}")
        elif cmd == "l":
            increase_speed()
            print(f"frame delay: {frame_delay}")
        elif cmd == "q":
            root.destroy()
            return


osc_thread = threading.Thread(target=run_osc, daemon=True)
osc_thread.start()

if os.getenv("DEBUG", "false") == "true":
    debug_thread = threading.Thread(target=debug_terminal, daemon=True)
    debug_thread.start()

root.attributes("-fullscreen", True)
root.configure(bg="black")
root.configure(cursor="none")

root.bind("<q>", lambda _: root.destroy())
root.bind("<Up>", lambda _: increase_width())
root.bind("<Down>", lambda _: decrease_width())
root.bind("<Right>", lambda _: increase_speed())
root.bind("<Left>", lambda _: decrease_speed())
root.bind("<o>", lambda _: decrease_mix())
root.bind("<p>", lambda _: increase_mix())

update_frame()
root.mainloop()

video.release()
cv2.destroyAllWindows()

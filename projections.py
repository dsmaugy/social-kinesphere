import tkinter as tk

import cv2
import numpy as np
from PIL import Image, ImageTk

DELAY = 60

video = cv2.VideoCapture("videos/art1.mp4")
if video.isOpened():
    print("Video Succefully opened")
else:
    print("Something went wrong check if the video name and path is correct")

root = tk.Tk()
root.title("Projections")

label = tk.Label(root)
label.pack()

projection_width = 800


def get_next_video_frame():
    global video
    ret, frame = video.read()
    if not ret:
        video.set(cv2.CAP_PROP_POS_FRAMES, 0)
        # assume that this will always work
        _, frame = video.read()

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
    global label

    frame = cv2.cvtColor(get_next_video_frame(), cv2.COLOR_BGR2RGB)
    frame = zoom_and_crop(frame, projection_width, root.winfo_screenheight())

    img = Image.fromarray(frame)
    imgtk = ImageTk.PhotoImage(image=img)

    label.imgtk = imgtk
    label.config(image=imgtk)

    root.after(DELAY, update_frame)


def increase_width():
    global projection_width
    projection_width = min(projection_width + 10, root.winfo_screenwidth())


def decrease_width():
    global projection_width
    projection_width = max(projection_width - 10, 0)


root.configure(bg="black")
root.bind("<q>", lambda _: root.destroy())
root.bind("<Up>", lambda _: increase_width())
root.bind("<Down>", lambda _: decrease_width())


update_frame()
root.mainloop()

video.release()
cv2.destroyAllWindows()

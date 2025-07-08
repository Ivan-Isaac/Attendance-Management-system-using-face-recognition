import tkinter as tk
from tkinter import *
import os, cv2
import shutil
import csv
import numpy as np
from PIL import ImageTk, Image
import pandas as pd
import datetime
import time
import tkinter.font as font
import pyttsx3

# project module
import show_attendance
import takeImage
import trainImage
import automaticAttedance


def text_to_speech(user_text):
    engine = pyttsx3.init()
    engine.say(user_text)
    engine.runAndWait()


# --- START OF PATH DEFINITIONS ---
haarcasecade_path = "haarcascade_frontalface_default.xml"

trainimagelabel_dir = "TrainingImageLabel"
trainimagelabel_path = os.path.join(".", trainimagelabel_dir, "Trainner.yml")

trainimage_dir = "TrainingImage"
trainimage_path = os.path.join(".", trainimage_dir)

studentdetail_dir = "StudentDetails"
studentdetail_path = os.path.join(".", studentdetail_dir, "studentdetails.csv")

attendance_path = "Attendance"

# Ensure all necessary base directories exist
if not os.path.exists(trainimage_path):
    os.makedirs(trainimage_path)

if not os.path.exists(os.path.join(".", trainimagelabel_dir)):
    os.makedirs(os.path.join(".", trainimagelabel_dir))

if not os.path.exists(os.path.join(".", studentdetail_dir)):
    os.makedirs(os.path.join(".", studentdetail_dir))
# --- END OF PATH DEFINITIONS ---


# --- START OF UI HELPER FUNCTIONS & CALLBACKS (MOVED HERE) ---

# to destroy screen
def del_sc1():
    sc1.destroy()


# error message for name and no
def err_screen():
    global sc1
    sc1 = tk.Tk()
    sc1.geometry("400x110")
    sc1.iconbitmap("AMS.ico") # Assuming AMS.ico is present
    sc1.title("Warning!!")
    sc1.configure(background="#1c1c1c")
    sc1.resizable(0, 0)
    tk.Label(
        sc1,
        text="Enrollment & Name required!!!",
        fg="yellow",
        bg="#1c1c1c",
        font=("Verdana", 16, "bold"),
    ).pack(pady=10)
    tk.Button(
        sc1,
        text="OK",
        command=del_sc1,
        fg="yellow",
        bg="#333333",
        activebackground="red",
        font=("Verdana", 16, "bold"),
    ).pack(pady=5)

def testVal(inStr, acttyp):
    if acttyp == "1":  # insert
        if not inStr.isdigit():
            return False
    return True

# --- TakeImageUI Function (Refactored to use grid) ---
def TakeImageUI():
    ImageUI = Tk()
    ImageUI.title("Take Student Image..")
    ImageUI.geometry("780x480")
    ImageUI.configure(background="#1c1c1c")
    ImageUI.resizable(True, True) # Allow resizing for grid to work

    # Configure ImageUI grid weights
    ImageUI.grid_rowconfigure(0, weight=1) # Title
    ImageUI.grid_rowconfigure(1, weight=1) # Heading
    ImageUI.grid_rowconfigure(2, weight=1) # Enrollment row
    ImageUI.grid_rowconfigure(3, weight=1) # Name row
    ImageUI.grid_rowconfigure(4, weight=1) # Notification row
    ImageUI.grid_rowconfigure(5, weight=2) # Buttons row (more space)
    ImageUI.grid_columnconfigure(0, weight=1) # Left column for labels
    ImageUI.grid_columnconfigure(1, weight=2) # Right column for entries/message

    # Title Bar
    titl_frame_image_ui = tk.Frame(ImageUI, bg="#1c1c1c", relief=RIDGE, bd=10)
    titl_frame_image_ui.grid(row=0, column=0, columnspan=2, sticky="ew", padx=10, pady=10)
    titl_frame_image_ui.grid_columnconfigure(0, weight=1) # Single column in frame

    titl_image_ui = tk.Label(
        titl_frame_image_ui, text="Register Your Face", bg="#1c1c1c", fg="green", font=("Verdana", 24, "bold"),
    )
    titl_image_ui.grid(row=0, column=0, sticky="ew") # fill frame

    # Heading
    a_image_ui = tk.Label(
        ImageUI,
        text="Enter the details",
        bg="#1c1c1c",
        fg="yellow",
        bd=10,
        font=("Verdana", 20, "bold"),
    )
    a_image_ui.grid(row=1, column=0, columnspan=2, sticky="ew", pady=10)

    # ER no
    lbl1 = tk.Label(
        ImageUI,
        text="Enrollment No",
        bg="#1c1c1c",
        fg="yellow",
        bd=5,
        relief=RIDGE,
        font=("Verdana", 12),
    )
    lbl1.grid(row=2, column=0, padx=10, pady=5, sticky="e")

    txt1 = tk.Entry(
        ImageUI,
        bd=5,
        validate="key",
        bg="#333333",
        fg="yellow",
        relief=RIDGE,
        font=("Verdana", 16, "bold"),
    )
    txt1.grid(row=2, column=1, padx=10, pady=5, sticky="ew")
    txt1["validatecommand"] = (txt1.register(testVal), "%P", "%d")

    # name
    lbl2 = tk.Label(
        ImageUI,
        text="Name",
        bg="#1c1c1c",
        fg="yellow",
        bd=5,
        relief=RIDGE,
        font=("Verdana", 12),
    )
    lbl2.grid(row=3, column=0, padx=10, pady=5, sticky="e")

    txt2 = tk.Entry(
        ImageUI,
        bd=5,
        bg="#333333",
        fg="yellow",
        relief=RIDGE,
        font=("Verdana", 16, "bold"),
    )
    txt2.grid(row=3, column=1, padx=10, pady=5, sticky="ew")

    lbl3 = tk.Label(
        ImageUI,
        text="Notification",
        bg="#1c1c1c",
        fg="yellow",
        bd=5,
        relief=RIDGE,
        font=("Verdana", 12),
    )
    lbl3.grid(row=4, column=0, padx=10, pady=5, sticky="e")

    message = tk.Label(
        ImageUI,
        bd=5,
        bg="#333333",
        fg="yellow",
        relief=RIDGE,
        font=("Verdana", 12, "bold"),
    )
    message.grid(row=4, column=1, padx=10, pady=5, sticky="ew")

    # Buttons (Row 5)
    button_frame = tk.Frame(ImageUI, bg="#1c1c1c")
    button_frame.grid(row=5, column=0, columnspan=2, pady=20)
    button_frame.grid_columnconfigure(0, weight=1)
    button_frame.grid_columnconfigure(1, weight=1)

    def take_image():
        l1 = txt1.get()
        l2 = txt2.get()
        takeImage.TakeImage(
            l1,
            l2,
            haarcasecade_path,
            trainimage_path,
            message,
            err_screen,
            text_to_speech,
        )
        txt1.delete(0, "end")
        txt2.delete(0, "end")

    takeImg = tk.Button(
        button_frame,
        text="Take Image",
        command=take_image,
        bd=10,
        font=("Verdana", 16, "bold"),
        bg="#333333",
        fg="yellow",
        relief=RIDGE,
    )
    takeImg.grid(row=0, column=0, padx=15, pady=5, sticky="nsew")

    def train_image():
        trainImage.TrainImage(
            haarcasecade_path,
            trainimage_path,
            trainimagelabel_path,
            message,
            text_to_speech,
        )

    trainImg = tk.Button(
        button_frame,
        text="Train Image",
        command=train_image,
        bd=10,
        font=("Verdana", 16, "bold"),
        bg="#333333",
        fg="yellow",
        relief=RIDGE,
    )
    trainImg.grid(row=0, column=1, padx=15, pady=5, sticky="nsew")

# Callbacks for main window buttons
def automatic_attedance():
    automaticAttedance.subjectChoose(text_to_speech)

def view_attendance():
    show_attendance.subjectchoose(text_to_speech)

# --- END OF UI HELPER FUNCTIONS & CALLBACKS ---


window = Tk() # Main window creation
window.title("Face Recognizer")
window.geometry("1280x720")
dialog_title = "QUIT"
dialog_text = "Are you sure want to close?"
window.configure(background="#1c1c1c")

# --- Configure main window grid weights for responsiveness ---
window.grid_rowconfigure(0, weight=1)
window.grid_rowconfigure(1, weight=2)
window.grid_rowconfigure(2, weight=3)
window.grid_rowconfigure(3, weight=2)
window.grid_rowconfigure(4, weight=1)
window.grid_columnconfigure(0, weight=1)
window.grid_columnconfigure(1, weight=1)
window.grid_columnconfigure(2, weight=1)

# --- UI Elements for Main Window ---

# Logo and Title
logo = Image.open("UI_Image/0001.png")
logo = logo.resize((50, 47), Image.LANCZOS)
logo1 = ImageTk.PhotoImage(logo)

titl_frame = tk.Frame(window, bg="#1c1c1c", relief=RIDGE, bd=10)
titl_frame.grid(row=0, column=0, columnspan=3, sticky="ew", padx=10, pady=10)
titl_frame.grid_columnconfigure(0, weight=1)
titl_frame.grid_columnconfigure(1, weight=3)

l1 = tk.Label(titl_frame, image=logo1, bg="#1c1c1c")
l1.grid(row=0, column=0, sticky="w", padx=10, pady=5)

titl = tk.Label(
    titl_frame, text="CLASS VISION", bg="#1c1c1c", fg="yellow", font=("Verdana", 24, "bold"),
)
titl.grid(row=0, column=1, sticky="w", padx=10, pady=5)

# Welcome Message
a = tk.Label(
    window,
    text="Welcome to CLASS VISION",
    bg="#1c1c1c",
    fg="yellow",
    bd=10,
    font=("Verdana", 28, "bold"),
)
a.grid(row=1, column=0, columnspan=3, sticky="nsew", pady=20)

# UI Images (Register, Verify, Attendance)
ri = Image.open("UI_Image/register.png")
r = ImageTk.PhotoImage(ri)
label1 = Label(window, image=r, bg="#1c1c1c")
label1.image = r
label1.grid(row=2, column=0, padx=20, pady=10)

vi = Image.open("UI_Image/verifyy.png")
v = ImageTk.PhotoImage(vi)
label3 = Label(window, image=v, bg="#1c1c1c")
label3.image = v
label3.grid(row=2, column=1, padx=20, pady=10)

ai = Image.open("UI_Image/attendance.png")
a_img = ImageTk.PhotoImage(ai)
label2 = Label(window, image=a_img, bg="#1c1c1c")
label2.image = a_img
label2.grid(row=2, column=2, padx=20, pady=10)


# --- Main Buttons (Row 3) ---
r_btn = tk.Button(
    window,
    text="Register a new student",
    command=TakeImageUI, # NOW TakeImageUI is defined above!
    bd=10,
    font=("Verdana", 14),
    bg="black",
    fg="yellow",
    relief=RIDGE,
)
r_btn.grid(row=3, column=0, pady=10, padx=10, sticky="nsew")

take_attend_btn = tk.Button(
    window,
    text="Take Attendance",
    command=automatic_attedance, # NOW automatic_attedance is defined above!
    bd=10,
    font=("Verdana", 14),
    bg="black",
    fg="yellow",
    relief=RIDGE,
)
take_attend_btn.grid(row=3, column=1, pady=10, padx=10, sticky="nsew")

view_attend_btn = tk.Button(
    window,
    text="View Attendance",
    command=view_attendance, # NOW view_attendance is defined above!
    bd=10,
    font=("Verdana", 14),
    bg="black",
    fg="yellow",
    relief=RIDGE,
)
view_attend_btn.grid(row=3, column=2, pady=10, padx=10, sticky="nsew")

# --- EXIT Button (Row 4) ---
exit_btn = tk.Button(
    window,
    text="EXIT",
    bd=10,
    command=quit,
    font=("Verdana", 16),
    bg="black",
    fg="yellow",
    relief=RIDGE,
)
exit_btn.grid(row=4, column=0, columnspan=3, pady=20, sticky="ew")


window.mainloop()
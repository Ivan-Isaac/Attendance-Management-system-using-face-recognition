import tkinter as tk # Keep this import for clarity, though 'from tkinter import *' is also present
from tkinter import * # This imports Tk, Label, Button, etc. directly
import os, cv2
import shutil
import csv
import numpy as np
from PIL import ImageTk, Image
import pandas as pd
import datetime
import time
import tkinter.ttk as tkk
import tkinter.font as font
import subprocess # Needed for opening folders on Linux (xdg-open)
import sys # <--- ADDED THIS IMPORT for sys.platform


# Correcting path separators to be platform-independent and consistent
haarcasecade_path = "haarcascade_frontalface_default.xml"
trainimagelabel_dir = "TrainingImageLabel"
trainimagelabel_path = os.path.join(".", trainimagelabel_dir, "Trainner.yml")
trainimage_dir = "TrainingImage"
trainimage_path = os.path.join(".", trainimage_dir) # Consistent use of os.path.join
studentdetail_dir = "StudentDetails"
studentdetail_path = os.path.join(".", studentdetail_dir, "studentdetails.csv")
attendance_root_dir = "Attendance" # Renamed to avoid confusion with attendance_path in FillAttendance

# Make sure these directories exist when the script runs
if not os.path.exists(os.path.dirname(trainimagelabel_path)): # Checks for TrainingImageLabel directory
    os.makedirs(os.path.dirname(trainimagelabel_path))
if not os.path.exists(os.path.dirname(studentdetail_path)): # Checks for StudentDetails directory
    os.makedirs(os.path.dirname(studentdetail_path))
if not os.path.exists(trainimage_path): # Checks for TrainingImage directory
    os.makedirs(trainimage_path)
if not os.path.exists(attendance_root_dir):
    os.makedirs(attendance_root_dir)


# for choose subject and fill attendance
def subjectChoose(text_to_speech):
    def FillAttendance():
        sub = tx.get()
        now = time.time()
        future = now + 20
        print(f"Starting attendance capture for {sub}...")
        print(f"Capture will end in 20 seconds at {time.ctime(future)}")

        if sub == "":
            t = "Please enter the subject name!!!"
            text_to_speech(t)
        else:
            try:
                recognizer = cv2.face.LBPHFaceRecognizer_create()
                try:
                    recognizer.read(trainimagelabel_path)
                except Exception as e: # Catch broader exception to show error
                    error_msg = f"Model not found or cannot be read: {e}. Please train the model."
                    Notifica.configure(
                        text=error_msg,
                        bg="black",
                        fg="yellow",
                        width=33,
                        font=("times", 15, "bold"),
                    )
                    Notifica.place(x=20, y=250)
                    text_to_speech(error_msg)
                    return # Exit if model not found

                facecasCade = cv2.CascadeClassifier(haarcasecade_path)
                
                try:
                    df = pd.read_csv(studentdetail_path)
                except FileNotFoundError:
                    error_msg = f"Student details file not found: {studentdetail_path}. Please register students."
                    Notifica.configure(
                        text=error_msg,
                        bg="black",
                        fg="yellow",
                        width=33,
                        font=("times", 15, "bold"),
                    )
                    Notifica.place(x=20, y=250)
                    text_to_speech(error_msg)
                    return # Exit if student details not found


                cam = cv2.VideoCapture(0)
                if not cam.isOpened():
                    error_msg = "Could not open webcam. Please ensure it's not in use."
                    Notifica.configure(
                        text=error_msg,
                        bg="black",
                        fg="yellow",
                        width=33,
                        font=("times", 15, "bold"),
                    )
                    Notifica.place(x=20, y=250)
                    text_to_speech(error_msg)
                    return

                font = cv2.FONT_HERSHEY_SIMPLEX
                col_names = ["Enrollment", "Name"]
                attendance = pd.DataFrame(columns=col_names)
                
                # Names lookup for recognized IDs
                names = {}
                for index, row in df.iterrows():
                    try:
                        # Convert the 'Enrollment' from CSV to an integer
                        # This ensures the dictionary keys are integers, matching recognizer output
                        enrollment_id_int = int(row['Enrollment'])
                        names[enrollment_id_int] = row['Name']
                        # --- MODIFICATION END ---
                    except ValueError:
                        print(f"Warning: Could not convert Enrollment '{row['Enrollment']}' to integer. Skipping this entry.")
                        # You might want to log this or handle it more explicitly for invalid data

                # print(f"Loaded names dictionary: {names}") # For debugging: uncomment to see populated names
                
                while True:
                    ret, im = cam.read()
                    if not ret:
                        print("Failed to grab frame, exiting attendance.")
                        break

                    gray = cv2.cvtColor(im, cv2.COLOR_BGR2GRAY)
                    faces = facecasCade.detectMultiScale(gray, 1.2, 5)

                    for (x, y, w, h) in faces:
                        Id, conf = recognizer.predict(gray[y : y + h, x : x + w])
                        
                        current_name = "Unknown"
                        display_color = (0, 25, 255) # Red for unknown

                        # --- MODIFICATION START ---
                        if conf < 70: # Confidence threshold for recognition
                            if Id in names: # Check if Id exists in the names dictionary (now with integer keys)
                                current_name = names[Id]
                                # Add to attendance DataFrame. Ensure Enrollment is stored consistently.
                                attendance.loc[len(attendance)] = [Id, current_name] 
                                display_color = (0, 260, 0) # Green for known
                            else:
                                current_name = f"Unknown ID" # If ID is recognized but not in names (e.g., new ID not in CSV)
                                cv2.putText(
                                    im,
                                    f"{current_name} ({Id})", # Display ID if it's an "Unknown ID" but a numerical ID was predicted
                                    (x, y - 10),
                                    font, 1, display_color, 2
                                )
                                # No attendance record for unknown IDs that are not in the CSV
                                continue # Skip to next face/frame if ID is unrecognized (not in CSV)

                        else: # conf >= 70, meaning confidence is too low for recognition
                            current_name = "Unknown" 
                            cv2.putText(
                                im,
                                current_name, # Just display "Unknown" if confidence is low
                                (x, y - 10),
                                font, 1, display_color, 2
                            )
                            # No attendance record for low confidence
                            continue # Skip to next face/frame if confidence is low

                        # This part will only execute for successfully recognized IDs (conf < 70 and Id in names)
                        cv2.rectangle(im, (x, y), (x + w, y + h), display_color, 4)
                        cv2.putText(
                            im,
                            f"{current_name} ({Id})", # Display Name and ID for known faces
                            (x, y - 10), # Position text above rectangle
                            font, 1, display_color, 2
                        )
                        # --- MODIFICATION END ---

                    if time.time() > future:
                        break

                    # Drop duplicates inside the loop to maintain a clean list of present students
                    attendance = attendance.drop_duplicates(["Enrollment"], keep="first")
                    
                    cv2.imshow("Filling Attendance...", im)
                    key = cv2.waitKey(30) & 0xFF
                    if key == 27: # ESC key
                        break

                cam.release()
                cv2.destroyAllWindows()
                
                # Ensure attendance has data before saving
                if attendance.empty:
                    f = "No faces detected or recognized during the session."
                    text_to_speech(f)
                    Notifica.configure(
                        text=f,
                        bg="black",
                        fg="yellow",
                        width=33,
                        relief=RIDGE,
                        bd=5,
                        font=("times", 15, "bold"),
                    )
                    Notifica.place(x=20, y=250)
                    return

                ts = time.time()
                today_date_str = datetime.datetime.fromtimestamp(ts).strftime("%Y-%m-%d")
                timeStamp = datetime.datetime.fromtimestamp(ts).strftime("%H:%M:%S")
                Hour, Minute, Second = timeStamp.split(":")
                
                # Mark attendance with 1 for the current date
                attendance[today_date_str] = 1 

                # Define path for subject-specific attendance
                path_to_subject_folder = os.path.join(attendance_root_dir, sub)
                if not os.path.exists(path_to_subject_folder):
                    os.makedirs(path_to_subject_folder)
                
                # Filename for this specific daily attendance CSV
                fileName = os.path.join(
                    path_to_subject_folder,
                    f"{sub}_{today_date_str}_{Hour}-{Minute}-{Second}.csv"
                )
                
                print(f"Final attendance DataFrame:\n{attendance}")
                attendance.to_csv(fileName, index=False)

                m = "Attendance Filled Successfully of " + sub
                Notifica.configure(
                    text=m,
                    bg="black",
                    fg="yellow",
                    width=33,
                    relief=RIDGE,
                    bd=5,
                    font=("times", 15, "bold"),
                )
                text_to_speech(m)
                Notifica.place(x=20, y=250)


                # --- Start of Displaying Daily Attendance in New Window (Modified) ---
                daily_attendance_root = Tk()
                daily_attendance_root.title("Daily Attendance of " + sub)
                daily_attendance_root.configure(background="black")

                # Set an initial geometry for the window
                daily_attendance_root.geometry("550x350") # Still a good starting size
                daily_attendance_root.resizable(True, True) # Make it resizable

                cs_file_path = fileName # Use the same fileName as saved above

                try:
                    with open(cs_file_path, newline="") as file:
                        reader = csv.reader(file)
                        
                        header = next(reader, None) 
                        if header:
                            num_columns = len(header)
                            # We still configure columns to expand, but fixed width on labels
                            # will override the expansion for the label itself, making cells fixed.
                            # However, if content exceeds fixed width, the column *can* still expand
                            # or text will wrap (if wraplength is set).
                            for i in range(num_columns):
                                daily_attendance_root.grid_columnconfigure(i, weight=1) 
                        else:
                            print(f"CSV file '{cs_file_path}' is empty or has no header.")
                            text_to_speech("Daily attendance file is empty.")
                            daily_attendance_root.destroy()
                            return
                        
                        # Define a common width for columns for Excel-like appearance
                        # You can adjust this value (e.g., 10, 15, 20) based on your content.
                        COLUMN_WIDTH = 15 # <-- ADJUST THIS VALUE FOR BOX SIZE

                        # Display header
                        for c_idx, head_item in enumerate(header):
                            label = Label(
                                daily_attendance_root,
                                fg="yellow",
                                font=("times", 15, "bold", "underline"),
                                bg="#333333",
                                text=head_item,
                                relief=RIDGE,
                                width=COLUMN_WIDTH # Apply fixed width to header
                            )
                            # Keep sticky for alignment within the fixed width cell
                            label.grid(row=0, column=c_idx, padx=2, pady=2, sticky="nsew") # Reduced padding

                        r = 1 # Start data rows from 1 (after header)
                        for col_data_row in reader:
                            daily_attendance_root.grid_rowconfigure(r, weight=1) # Each row expands
                            c = 0
                            for item_value in col_data_row:
                                label = Label(
                                    daily_attendance_root,
                                    fg="yellow",
                                    font=("times", 20, "bold"), # <-- INCREASED FONT SIZE FOR NUMBERS
                                    bg="black",
                                    text=item_value,
                                    relief=RIDGE,
                                    width=COLUMN_WIDTH, # <-- APPLY FIXED WIDTH HERE TOO
                                    wraplength=COLUMN_WIDTH * 8 # Optional: adjust wraplength based on new width
                                )
                                label.grid(row=r, column=c, padx=2, pady=2, sticky="nsew") # Reduced padding
                                c += 1
                            r += 1
                    
                    if r == 1: # Only header was displayed (r started at 1, so if it's still 1, no data rows)
                         print(f"CSV file '{cs_file_path}' contains only headers, no data rows.")
                         text_to_speech("No student data found for this attendance session.")


                except FileNotFoundError:
                    f_error = f"Error: Daily attendance file not found at {cs_file_path}"
                    print(f_error)
                    text_to_speech(f_error)
                    daily_attendance_root.destroy()
                    return
                except Exception as e:
                    f_error = f"An error occurred while displaying attendance: {e}"
                    print(f"Error Type: {type(e).__name__}, Message: {e}") # Added more error detail
                    text_to_speech(f_error)
                    daily_attendance_root.destroy()
                    return

                daily_attendance_root.mainloop()
                # --- End of Displaying Daily Attendance in New Window ---

            except Exception as e: # General error during the attendance process
                f = f"An error occurred during attendance: {e}"
                text_to_speech(f)
                cv2.destroyAllWindows()
                Notifica.configure(
                    text=f,
                    bg="black",
                    fg="yellow",
                    width=33,
                    relief=RIDGE,
                    bd=5,
                    font=("times", 15, "bold"),
                )
                Notifica.place(x=20, y=250)


    ### windo is frame for subject chooser
    subject = Tk()
    subject.title("Subject...")
    subject.geometry("580x320")
    subject.resizable(0, 0) # Keep this window non-resizable as it uses place()
    subject.configure(background="black")

    titl = tk.Label(subject, bg="black", relief=RIDGE, bd=10, font=("arial", 30))
    titl.pack(fill=X)

    titl = tk.Label(
        subject,
        text="Enter the Subject Name",
        bg="black",
        fg="green",
        font=("arial", 25),
    )
    titl.place(x=160, y=12) # This window still uses .place()

    Notifica = tk.Label( # Define Notifica here as well for this window
        subject,
        text="Attendance filled Successfully",
        bg="yellow",
        fg="black",
        width=33,
        height=2,
        font=("times", 15, "bold"),
    )
    # Notifica will be placed by FillAttendance or Attf functions

    def Attf():
        sub = tx.get()
        if sub == "":
            t = "Please enter the subject name!!!"
            text_to_speech(t)
        else:
            folder_to_open = os.path.join(attendance_root_dir, sub) # Use attendance_root_dir
            if os.path.exists(folder_to_open):
                try:
                    # For Windows
                    if os.name == 'nt': # 'nt' is for Windows
                        os.startfile(folder_to_open)
                    # For macOS
                    elif sys.platform == 'darwin': 
                        subprocess.Popen(['open', folder_to_open])
                    # For Linux (most common desktop environments)
                    elif sys.platform.startswith('linux'):
                        subprocess.Popen(['xdg-open', folder_to_open])
                    else:
                        print(f"Unsupported OS for opening folder automatically: {sys.platform}")
                        text_to_speech("Unsupported operating system for this feature.")

                except FileNotFoundError:
                    print(f"Error: Command to open folder not found. Cannot open folder {folder_to_open}")
                    text_to_speech(f"Cannot open folder for {sub}.")
                except Exception as e:
                    print(f"An unexpected error occurred trying to open folder: {e}")
                    text_to_speech(f"Error opening folder for {sub}.")
            else:
                print(f"Folder not found: {folder_to_open}")
                text_to_speech(f"Attendance folder for {sub} not found.")

    attf = tk.Button(
        subject,
        text="Check Sheets",
        command=Attf,
        bd=7,
        font=("times new roman", 15),
        bg="black",
        fg="yellow",
        height=2,
        width=10,
        relief=RIDGE,
    )
    attf.place(x=360, y=170)

    sub_label = tk.Label( # Renamed variable to avoid conflict with `sub` string
        subject,
        text="Enter Subject",
        width=10,
        height=2,
        bg="black",
        fg="yellow",
        bd=5,
        relief=RIDGE,
        font=("times new roman", 15),
    )
    sub_label.place(x=50, y=100)

    tx = tk.Entry(
        subject,
        width=15,
        bd=5,
        bg="black",
        fg="yellow",
        relief=RIDGE,
        font=("times", 30, "bold"),
    )
    tx.place(x=190, y=100)

    fill_a = tk.Button(
        subject,
        text="Fill Attendance",
        command=FillAttendance,
        bd=7,
        font=("times new roman", 15),
        bg="black",
        fg="yellow",
        height=2,
        width=12,
        relief=RIDGE,
    )
    fill_a.place(x=195, y=170)
    subject.mainloop()
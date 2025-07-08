import pandas as pd
from glob import glob
import os # Import os for os.path.join
import tkinter
import csv
import tkinter as tk
from tkinter import *

def subjectchoose(text_to_speech):
    def calculate_attendance():
        Subject = tx.get()
        if Subject=="":
            t='Please enter the subject name.'
            text_to_speech(t)
            return # Exit if subject is empty

        # IMPORTANT: Use os.path.join for platform-independent paths with glob
        # Also, your attendance files are named like "Subject_DATE_TIME.csv"
        # So the pattern should look for that.
        # Example filename: Attendance/Math/Math_2025-07-08_12-00-00.csv
        search_pattern = os.path.join("Attendance", Subject, f"{Subject}_*.csv")
        filenames = glob(search_pattern)

        if not filenames:
            # Handle the case where no attendance files are found for the subject
            t = f"No attendance records found for subject: {Subject}"
            print(t) # For debugging
            text_to_speech(t)
            # You might want to display a message to the user in the Tkinter window
            # For example:
            Notifica.configure(
                text=t,
                bg="black",
                fg="red",
                width=33,
                font=("times", 15, "bold"),
            )
            Notifica.place(x=100, y=250) # Assuming Notifica label exists and is in scope
            return

        df = [pd.read_csv(f) for f in filenames]

        newdf = df[0]
        for i in range(1, len(df)):
            newdf = newdf.merge(df[i], how="outer")
        newdf.fillna(0, inplace=True)
        newdf["Attendance"] = 0
        for i in range(len(newdf)):
            # Assuming 'Enrollment' and 'Name' are the first two columns (index 0 and 1)
            # and actual attendance data starts from index 2.
            # newdf.iloc[i, 2:-1] slices from the 3rd column up to (but not including) the last column.
            # This logic assumes your attendance columns are date-stamped and are after Name.
            newdf["Attendance"].iloc[i] = str(int(round(newdf.iloc[i, 2:-1].mean() * 100)))+'%'
            #newdf.sort_values(by=['Enrollment'],inplace=True)

        # IMPORTANT: Save the attendance summary file using os.path.join
        output_path = os.path.join("Attendance", Subject, "attendance.csv")
        newdf.to_csv(output_path, index=False)

        root = tkinter.Tk()
        root.title("Attendance of "+Subject)
        root.configure(background="black")
        # IMPORTANT: Open the summary CSV using os.path.join
        cs = os.path.join("Attendance", Subject, "attendance.csv")

        # Make sure the file exists before trying to open it in CSV reader
        if not os.path.exists(cs):
            t = f"Consolidated attendance file not found: {cs}"
            print(t)
            text_to_speech(t)
            root.destroy() # Close the empty Tkinter window
            return

        with open(cs) as file:
            reader = csv.reader(file)
            r = 0

            for col in reader:
                c = 0
                for row in col:

                    label = tkinter.Label(
                        root,
                        width=10,
                        height=1,
                        fg="yellow",
                        font=("times", 15, " bold "),
                        bg="black",
                        text=row,
                        relief=tkinter.RIDGE,
                    )
                    label.grid(row=r, column=c)
                    c += 1
                r += 1
        root.mainloop()
        print(newdf)

    subject = Tk()
    # windo.iconbitmap("AMS.ico")
    subject.title("Subject...")
    subject.geometry("580x320")
    subject.resizable(0, 0)
    subject.configure(background="black")

    # Add a Notification Label here as it's used in calculate_attendance for error messages
    Notifica = tk.Label(
        subject,
        text="", # Initially empty
        bg="black",
        fg="yellow",
        width=33,
        height=2,
        font=("times", 15, "bold"),
    )
    # Notifica.place(x=100, y=250) # You can place it here if you want it visible by default

    titl = tk.Label(subject, bg="black", relief=RIDGE, bd=10, font=("arial", 30))
    titl.pack(fill=X)

    titl = tk.Label(
        subject,
        text="Which Subject of Attendance?",
        bg="black",
        fg="green",
        font=("arial", 25),
    )
    titl.place(x=100, y=12)

    def Attf():
        sub = tx.get()
        if sub == "":
            t="Please enter the subject name!!!"
            text_to_speech(t)
        else:
            # IMPORTANT: Use os.path.join for cross-platform compatibility
            folder_to_open = os.path.join("Attendance", sub)
            if os.path.exists(folder_to_open):
                import subprocess
                try:
                    subprocess.Popen(['xdg-open', folder_to_open])
                except FileNotFoundError:
                    print(f"Error: xdg-open not found. Cannot open folder {folder_to_open}")
                    text_to_speech(f"Cannot open folder. xdg-open not found.")
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

    sub = tk.Label(
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
    sub.place(x=50, y=100)

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
        text="View Attendance",
        command=calculate_attendance,
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
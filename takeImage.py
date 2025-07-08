import csv
import os, cv2
import numpy as np
import pandas as pd # Used for robust student existence check
import datetime
import time

# take Image of user
def TakeImage(l1, l2, haarcasecade_path, trainimage_path, message, err_screen, text_to_speech):
    if (l1 == "") and (l2==""):
        t='Please Enter your Enrollment Number and Name.'
        text_to_speech(t)
        message.configure(text=t) # Update message in UI
    elif l1=='':
        t='Please Enter your Enrollment Number.'
        text_to_speech(t)
        message.configure(text=t) # Update message in UI
    elif l2 == "":
        t='Please Enter your Name.'
        text_to_speech(t)
        message.configure(text=t) # Update message in UI
    else:
        try:
            cam = cv2.VideoCapture(0)
            if not cam.isOpened():
                error_msg = "Could not open webcam. Please ensure it's not in use."
                message.configure(text=error_msg)
                text_to_speech(error_msg)
                return

            detector = cv2.CascadeClassifier(haarcasecade_path)
            Enrollment = str(l1) # Ensure Enrollment is treated as a string for consistency with file paths
            Name = str(l2)       # Ensure Name is treated as a string

            # --- Check for existing student and create directory ---
            student_details_file = "StudentDetails/studentdetails.csv"
            
            # Check if student already exists in CSV
            student_already_exists = False
            if os.path.exists(student_details_file):
                try:
                    # Read the CSV with header=None and names, similar to automaticAttendance.py
                    # This allows it to work even if the CSV currently lacks headers
                    temp_df = pd.read_csv(student_details_file, header=None, names=['Enrollment', 'Name'])
                    # Convert 'Enrollment' column to string to match 'Enrollment' variable
                    if Enrollment in temp_df['Enrollment'].astype(str).values:
                        student_already_exists = True
                except Exception as e:
                    print(f"Warning: Could not read {student_details_file} to check for existing student: {e}")
                    # If reading fails, assume student doesn't exist for now to proceed,
                    # but it's good to log this warning.

            if student_already_exists:
                t = f"Student with Enrollment No. {Enrollment} already exists!"
                message.configure(text=t)
                text_to_speech(t)
                cam.release()
                cv2.destroyAllWindows()
                return # Exit if student already exists

            # Proceed only if student does not exist in CSV
            directory = Enrollment + "_" + Name
            path = os.path.join(trainimage_path, directory)

            # Create the student's image directory. If it somehow already exists, it's fine.
            os.makedirs(path, exist_ok=True) # exist_ok=True prevents error if dir exists

            sampleNum = 0
            message.configure(text="Capturing images...") # Give feedback to user
            
            while True:
                ret, img = cam.read()
                if not ret:
                    print("Failed to grab frame. Exiting image capture.")
                    break

                gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
                faces = detector.detectMultiScale(gray, 1.3, 5)
                for (x, y, w, h) in faces:
                    cv2.rectangle(img, (x, y), (x + w, y + h), (255, 0, 0), 2)
                    
                    # Only save image if a face is detected
                    if w > 0 and h > 0:
                        sampleNum = sampleNum + 1
                        image_filename = f"{Name}_{Enrollment}_{sampleNum}.jpg"
                        cv2.imwrite(
                            os.path.join(path, image_filename), # Use os.path.join for platform independence
                            gray[y : y + h, x : x + w],
                        )
                        cv2.putText(img, f"Images Captured: {sampleNum}/50", (x, y-10), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
                    
                    cv2.imshow("Capturing Face...", img) # Changed window title for clarity
                
                key = cv2.waitKey(1) & 0xFF
                if key == ord("q"):
                    break
                elif sampleNum >= 50: # Changed to >= to ensure exactly 50 images are captured
                    break
            
            cam.release()
            cv2.destroyAllWindows()

            # --- CSV File Writing Logic ---
            # Define header row
            csv_headers = ['Enrollment', 'Name']
            row_to_write = [Enrollment, Name]
            
            # Check if the CSV file exists and is not empty.
            # We re-check file existence right before writing, in case it was deleted
            # during the image capture process (unlikely but good for robustness).
            file_exists_and_has_content = os.path.exists(student_details_file) and os.path.getsize(student_details_file) > 0

            with open(student_details_file, "a", newline='') as csvFile: # 'a' for append, 'newline=' for no blank rows
                writer = csv.writer(csvFile, delimiter=",")
                
                # Write headers ONLY if the file is new or currently empty (no headers)
                if not file_exists_and_has_content:
                    writer.writerow(csv_headers)
                
                writer.writerow(row_to_write)
            
            res = f"Images Saved for ER No: {Enrollment} Name: {Name}. Student details added to CSV."
            message.configure(text=res)
            text_to_speech(res)

        except Exception as e:
            error_message = f"An error occurred during image capture or registration: {e}"
            message.configure(text=error_message)
            text_to_speech(error_message)
            print(f"DEBUG ERROR: {e}") # Print error to console for debugging

            # Ensure webcam and windows are released even if an error occurs
            if 'cam' in locals() and cam.isOpened():
                cam.release()
            cv2.destroyAllWindows()
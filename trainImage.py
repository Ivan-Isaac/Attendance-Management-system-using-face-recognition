import csv
import os, cv2
import numpy as np
import pandas as pd
import datetime
import time
from PIL import ImageTk, Image


# Train Image
def TrainImage(haarcasecade_path, trainimage_path, trainimagelabel_path, message, text_to_speech):
    recognizer = cv2.face.LBPHFaceRecognizer_create()
    detector = cv2.CascadeClassifier(haarcasecade_path) # Not strictly needed for training, but kept as in original
    
    # Get images and labels from the modified function
    faces, Ids = getImagesAndLables(trainimage_path)
    
    if len(faces) == 0:
        error_msg = "No images found or processed for training. Please ensure students are registered and images are captured."
        message.configure(text=error_msg)
        text_to_speech(error_msg)
        print(error_msg) # For console debugging
        return
    
    # OpenCV's LBPHFaceRecognizer needs at least two samples to train.
    # If you have only one student registered, you might still hit this error.
    # It's highly recommended to register at least two distinct students before training.
    if len(np.unique(Ids)) < 2: # Check for at least two *unique* IDs
        error_msg = "Need more than one unique student (ID) to train the model. Please register at least two students."
        message.configure(text=error_msg)
        text_to_speech(error_msg)
        print(error_msg) # For console debugging
        return

    try:
        recognizer.train(faces, np.array(Ids)) # Pass Ids directly, it's already a list of ints
        recognizer.save(trainimagelabel_path)
        res = "Image Trained successfully!"
        message.configure(text=res)
        text_to_speech(res)
    except Exception as e:
        error_msg = f"Error during training: {e}. Ensure you have at least two unique student samples."
        message.configure(text=error_msg)
        text_to_speech(error_msg)
        print(f"Training error: {e}")


def getImagesAndLables(path):
    faces = []
    Ids = []
    imagePaths = []

    # --- MODIFICATION START ---
    # Recursively walk through all subdirectories to find image files
    for root, dirs, files in os.walk(path):
        for file_name in files:
            # Check for common image extensions
            if file_name.lower().endswith((".jpg", ".jpeg", ".png")):
                imagePaths.append(os.path.join(root, file_name))
    # --- MODIFICATION END ---

    if not imagePaths:
        print(f"No valid image files found in '{path}' or its subdirectories. Please ensure images are captured and placed in student-specific subfolders like 'TrainingImage/Enrollment_Name/'.")
        return [], [] # Return empty lists if no images are found

    print(f"Found {len(imagePaths)} images for training.") # Debugging line
    for imagePath in imagePaths:
        try:
            pilImage = Image.open(imagePath).convert("L") # Convert to grayscale
            imageNp = np.array(pilImage, "uint8")

            # --- MODIFICATION START ---
            # Extract ID from filename: Name_Enrollment_SampleNum.jpg
            # Example filename: Ivan_1_1.jpg --> parts will be ['Ivan', '1', '1.jpg']
            filename = os.path.basename(imagePath) # Get just the filename (e.g., Ivan_1_1.jpg)
            parts = filename.split("_")
            
            if len(parts) >= 2: # Ensure there are enough parts to get the enrollment ID
                Id = int(parts[1]) # Enrollment ID is the second part (index 1)
                faces.append(imageNp)
                Ids.append(Id)
            else:
                print(f"Skipping malformed filename: '{filename}'. Expected format 'Name_Enrollment_SampleNum.jpg'")
            # --- MODIFICATION END ---

        except ValueError: # Catches error if parts[1] is not a valid integer
            print(f"Skipping image '{imagePath}': Could not convert extracted ID to integer. Check filename format (Name_Enrollment_SampleNum.jpg).")
        except Exception as e:
            print(f"Error processing image '{imagePath}': {e}. Skipping this image.")
            continue # Skip to the next image if there's an error with this one
    
    print(f"Processed {len(faces)} faces and {len(Ids)} IDs for training.") # Debugging line
    return faces, Ids
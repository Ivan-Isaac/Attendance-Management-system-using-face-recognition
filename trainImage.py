import csv
import os, cv2
import numpy as np
import pandas as pd
import datetime
import time
from PIL import ImageTk, Image


# Train Image
def TrainImage(haarcasecade_path, trainimage_path, trainimagelabel_path, message,text_to_speech):
    recognizer = cv2.face.LBPHFaceRecognizer_create()
    detector = cv2.CascadeClassifier(haarcasecade_path)
    faces, Id = getImagesAndLables(trainimage_path)
    recognizer.train(faces, np.array(Id))
    recognizer.save(trainimagelabel_path)
    res = "Image Trained successfully"  # +",".join(str(f) for f in Id)
    message.configure(text=res)
    text_to_speech(res)


def getImagesAndLables(path):
    faces = []
    Ids = []
    # Get all file paths directly within the 'path' directory
    imagePaths = [os.path.join(path, f) for f in os.listdir(path) if os.path.isfile(os.path.join(path, f))]

    if not imagePaths:
        print(f"No images found in {path}. Please ensure images are placed directly in this directory.")
        return [], [] # Return empty lists if no images are found

    for imagePath in imagePaths:
        try:
            pilImage = Image.open(imagePath).convert("L")
            imageNp = np.array(pilImage, "uint8")
            # Assuming the ID is part of the filename, e.g., '1_Name_...'
            # This line extracts the ID from the filename.
            # Example: '1_Ivan_Ivan_1_18.jpg' -> splits by '_' -> ['1', 'Ivan', 'Ivan', '1', '18.jpg']
            # Then takes the second element (index 1) which is the first '1' (the ID)
            Id = int(os.path.split(imagePath)[-1].split("_")[0]) # Changed index from 1 to 0 for the first ID
            faces.append(imageNp)
            Ids.append(Id)
        except Exception as e:
            print(f"Error processing image {imagePath}: {e}")
            continue # Skip to the next image if there's an error with this one

    return faces, Ids
import cv2
import os
import sqlite3
import numpy as np
from deepface import DeepFace
from config import SNAPSHOT_DIR, EMBEDDING_MODEL, DATABASE_PATH
from recognizer.face_utilits import mark_attendance

def recognize_frame_by_class(frame, class_name):
    recognized = set()


    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM students WHERE class = ?", (class_name,))
    students_in_class = set(row[0] for row in cursor.fetchall())
    conn.close()


    known_faces = []
    for file in os.listdir(SNAPSHOT_DIR):
        name = os.path.splitext(file)[0]
        if name in students_in_class and file.lower().endswith((".jpg", ".jpeg", ".png")):
            path = os.path.join(SNAPSHOT_DIR, file)
            known_faces.append((name, path))

    if not known_faces:
        return "No known faces found for this class."


    face_detector = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    faces = face_detector.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5)

    if len(faces) == 0:
        return "No faces detected in the frame."


    for (x, y, w, h) in faces:
        face_img = frame[y:y+h, x:x+w]
        for name, known_path in known_faces:
            try:
                result = DeepFace.verify(face_img, known_path, model_name=EMBEDDING_MODEL, enforce_detection=False)
                if result["verified"]:
                    if name not in recognized:
                        mark_attendance(name)
                        recognized.add(name)
            except Exception as e:
                print(f"[ERROR] Comparing to {name}: {e}")

    return f"Recognized: {', '.join(recognized) if recognized else 'No match found'}"

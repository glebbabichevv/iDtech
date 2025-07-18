import os
import sqlite3
from deepface import DeepFace
from config import SNAPSHOT_DIR, EMBEDDING_MODEL, DATABASE_PATH
from recognizer.face_utilits import mark_attendance

def run():
    print("[INFO] Recognition started. Press 'q' to quit.")

    if not os.path.exists(SNAPSHOT_DIR):
        print("[ERROR] snapshots folder not found.")
        return

    known_faces = []
    for file in os.listdir(SNAPSHOT_DIR):
        if file.lower().endswith((".jpg", ".jpeg", ".png")):
            name = os.path.splitext(file)[0]
            path = os.path.join(SNAPSHOT_DIR, file)
            known_faces.append((name, path))

    if not known_faces:
        print("[ERROR] No faces found in snapshots.")
        return

    import cv2
    cap = cv2.VideoCapture(0)
    recognized = set()

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        cv2.imshow("Recognize", frame)
        key = cv2.waitKey(1) & 0xFF
        if key == ord("q"):
            break

        for name, known_path in known_faces:
            try:
                result = DeepFace.verify(frame, known_path, model_name=EMBEDDING_MODEL, enforce_detection=False)
                if result["verified"] and name not in recognized:
                    print(f"[INFO] {name} is present.")
                    mark_attendance(name)
                    recognized.add(name)
            except Exception as e:
                print(f"[ERROR] {e}")

    cap.release()
    cv2.destroyAllWindows()

def recognize_frame_by_class(frame, class_name):
    recognized = set()

    # Получаем имена студентов, относящихся к выбранному классу (только из таблицы students)
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM students WHERE class = ?", (class_name,))
    students_in_class = set(row[0] for row in cursor.fetchall())
    conn.close()

    # Используем только те фото, которые реально есть для студентов этого класса
    known_faces = []
    for file in os.listdir(SNAPSHOT_DIR):
        name = os.path.splitext(file)[0]
        if name in students_in_class and file.lower().endswith((".jpg", ".jpeg", ".png")):
            path = os.path.join(SNAPSHOT_DIR, file)
            known_faces.append((name, path))

    if not known_faces:
        return "No known faces found for this class."
    for name, known_path in known_faces:
        try:
            result = DeepFace.verify(frame, known_path, model_name=EMBEDDING_MODEL, enforce_detection=False)
            if result["verified"]:
                mark_attendance(name)
                recognized.add(name)
        except Exception as e:
            print(f"[ERROR] {e}")

    return f"Recognized: {', '.join(recognized) if recognized else 'No match found'}"

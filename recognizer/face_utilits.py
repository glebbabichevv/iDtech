import sqlite3
import os
import numpy as np
from deepface import DeepFace
from config import DATABASE_PATH, EMBEDDING_MODEL
import cv2

def ensure_db():
    os.makedirs(os.path.dirname(DATABASE_PATH), exist_ok=True)
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS students (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            class TEXT NOT NULL,
            embedding BLOB
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS classes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE
        )
    """)

    conn.commit()
    conn.close()

def reset_students_table():
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM students")
    cursor.execute("DELETE FROM sqlite_sequence WHERE name='students'")
    conn.commit()
    conn.close()

def get_all_classes():
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM classes ORDER BY name")
    classes = [row[0] for row in cursor.fetchall()]
    conn.close()
    return classes

def add_class(class_name):
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    try:
        cursor.execute("INSERT INTO classes (name) VALUES (?)", (class_name,))
        conn.commit()
    except sqlite3.IntegrityError:
        pass
    conn.close()

def remove_class(class_name):
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM classes WHERE name = ?", (class_name,))
    conn.commit()
    conn.close()

def save_student(name, class_name, embedding):
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    cursor.execute("INSERT INTO students (name, class, embedding) VALUES (?, ?, ?)",
                   (name, class_name, embedding.tobytes()))
    conn.commit()
    conn.close()

def get_embedding(frame):
    obj = DeepFace.represent(frame, model_name=EMBEDDING_MODEL, enforce_detection=False)
    if obj:
        return np.array(obj[0]['embedding'], dtype=np.float32)
    return None

def load_students():
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT id, name, class FROM students")
    data = cursor.fetchall()
    conn.close()
    return data

def mark_attendance(name):
    from config import ATTENDANCE_CSV, DATABASE_PATH
    import datetime
    import sqlite3
    import csv, os

    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT class FROM students WHERE name = ?", (name,))
    row = cursor.fetchone()
    conn.close()
    class_name = row[0] if row else "Unknown"

    date = datetime.date.today().isoformat()
    time = datetime.datetime.now().strftime("%H:%M:%S")
    os.makedirs(os.path.dirname(ATTENDANCE_CSV), exist_ok=True)
    with open(ATTENDANCE_CSV, 'a', newline='') as f:
        writer = csv.writer(f)
        writer.writerow([name, class_name, date, time])

import sqlite3

from config import DATABASE_PATH


def run():
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()

    cursor.execute("SELECT id, name, class FROM students")
    rows = cursor.fetchall()

    if rows:
        for row in rows:
            print(f"ID: {row[0]} | Name: {row[1]} | Class: {row[2]}")
    else:
        print("No students found.")

    conn.close()

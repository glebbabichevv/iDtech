import os
import csv
from config import ATTENDANCE_CSV

def run():



    with open(ATTENDANCE_CSV, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["Name", "Time"])
    print("[INFO] Attendance CSV has been reset.")

import cv2
import os
from config import SNAPSHOT_DIR
from recognizer.face_utilits import ensure_db, save_student, get_embedding

def run(name, class_name):
    ensure_db()

    os.makedirs(SNAPSHOT_DIR, exist_ok=True)
    save_path = os.path.join(SNAPSHOT_DIR, f"{name}.jpg")

    cap = cv2.VideoCapture(0)
    print("[INFO] Press 's' to capture face, 'q' to quit")
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        cv2.imshow("Add Student", frame)
        key = cv2.waitKey(1) & 0xFF
        if key == ord("s"):
            cv2.imwrite(save_path, frame)
            print(f"[INFO] Saved: {save_path}")
            embedding = get_embedding(frame)
            if embedding is not None:
                save_student(name, class_name, embedding)
            break
        elif key == ord("q"):
            break
    cap.release()
    cv2.destroyAllWindows()

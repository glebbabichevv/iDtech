from recognizer.face_utilits import reset_students_table
from recognizer.logger import logger

def run():
    reset_students_table()
    logger.info("Student database has been reset.")

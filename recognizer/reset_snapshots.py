import os
from config import SNAPSHOT_DIR
from recognizer.logger import logger

def run():
    if not os.path.exists(SNAPSHOT_DIR):
        logger.warning(f"Snapshot folder '{SNAPSHOT_DIR}' does not exist.")
        return

    deleted = 0
    for file in os.listdir(SNAPSHOT_DIR):
        file_path = os.path.join(SNAPSHOT_DIR, file)
        if os.path.isfile(file_path):
            os.remove(file_path)
            deleted += 1

    logger.info(f"Snapshot folder cleared. Deleted {deleted} file(s).")
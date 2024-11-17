from datetime import datetime, timezone
import time
from huggingface_hub import HfFileSystem
fs = HfFileSystem()

def rm_old_file(k_days=30):
    # List all files in a directory
    files = fs.ls("datasets/nichetensor-org/open-category/images", detail=False)
    start = time.time()
    print(time.time()-start)
    # Delete files older than k_days
    for file in files:
        last_commit_date = fs.info(files[0])['last_commit'].date
        if (datetime.now(timezone.utc) - last_commit_date).days > k_days:
            fs.rm(file)
            print(f"Deleted file: {file}")
    print('---------------')

try:
    while True:
        rm_old_file()
        # sleep for 1 hour
        time.sleep(3600)
except KeyboardInterrupt:
    print("Stopped by the user.")

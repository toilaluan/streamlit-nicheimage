import time
from huggingface_hub import HfFileSystem
fs = HfFileSystem()

def rm_old_file():
    # List all files in a directory
    files = fs.ls("datasets/nichetensor-org/open-category/images", detail=False)
    start = time.time()
    sorted_files = sorted(files, key=lambda y: fs.info(y)['last_commit'].date)
    print(time.time()-start)
    # Delete the oldest 100 files
    for y in sorted_files[:100]:
        fs.rm(y)
    print('---------------')

try:
    while True:
        rm_old_file()
        # sleep for 1 hour
        time.sleep(3600)
except KeyboardInterrupt:
    print("Stopped by the user.")

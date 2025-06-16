from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import subprocess
import os
import time

class ChangeHandler(FileSystemEventHandler):
    def __init__(self, restart_callback):
        self.restart_callback = restart_callback

    def on_modified(self, event):
        if event.src_path.endswith((".py", ".yaml", ".cfg")):
            self.restart_callback()

def restart_server():
    global process
    process.terminate()
    process = subprocess.Popen(["python", "main.py"])

if __name__ == "__main__":
    path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
    event_handler = ChangeHandler(restart_callback=restart_server)
    observer = Observer()
    observer.schedule(event_handler, path, recursive=True)
    observer.start()
    process = subprocess.Popen(["python", "main.py"])
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()

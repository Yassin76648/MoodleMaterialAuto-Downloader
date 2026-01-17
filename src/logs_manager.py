import os
import json

LOG_FILE = 'download_history.json'

def get_history():
    if os.path.exists(LOG_FILE):
        with open(LOG_FILE, "r") as f:
            return json.load(f)
    return {}

def update_history(url, file_name):
    history = get_history()
    history[url] = file_name

    with open(LOG_FILE, "w") as f:
        json.dump(history, f, indent=4)

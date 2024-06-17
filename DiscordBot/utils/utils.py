import json
import os

def load_ids():
    if not os.path.exists('data'):
        os.makedirs('data')
    try:
        with open('data/ids.json', 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return {}

def save_ids(updated_ids):
    current_ids = load_ids()
    current_ids.update(updated_ids)
    with open('data/ids.json', 'w') as f:
        json.dump(current_ids, f)

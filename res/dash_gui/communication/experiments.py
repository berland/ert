import orjson
import requests
from websockets.sync.client import connect


# Function to fetch data from the REST server
def fetch_experiments_data():
    url = "http://0.0.0.0:8000/experiments"
    try:
        response = requests.get(url)
        if response.status_code == 200:
            # Assuming the response is a JSON list of experiments
            experiments = response.json()
            print(experiments)
            return experiments
        else:
            print(f"Failed to fetch data, status code: {response.status_code}")
            return []
    except Exception as e:
        print(f"Error fetching data: {e}")
        return []


def fetch_events(experiment_id):
    url = f"ws://127.0.0.1:8000/experiments/{experiment_id}/events"
    with connect(url) as ws:
        while True:
            raw_msg = ws.recv()
            msg = orjson.loads(raw_msg)
            print(msg)
            if msg["event_type"] == "EndEvent":
                break


fetch_events("d28e1957-d7b0-4abd-b88a-cc69036c257b")

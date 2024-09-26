import requests


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

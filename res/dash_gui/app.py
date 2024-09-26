import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import dash_table
import requests
import pandas as pd

# Initialize the Dash app
app = dash.Dash(__name__)

# Define the layout of the app
app.layout = html.Div([
    html.H1("Experiments Dashboard"),

    # Button to refresh the data
    html.Button("Refresh Data", id="refresh-button", n_clicks=0),

    # Table to display the experiments data
    dash_table.DataTable(
        id='experiments-table',
        columns=[{"name": i, "id": i} for i in ['id', 'name', 'description']],
        data=[],  # Empty initially
    ),

    # Interval to auto-refresh the data every 10 seconds
    dcc.Interval(
        id='interval-component',
        interval=10 * 1000,  # Refresh every 10 seconds
        n_intervals=0
    )
])


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


# Callback to update the table with new data
@app.callback(
    Output('experiments-table', 'data'),
    [Input('refresh-button', 'n_clicks'),
     Input('interval-component', 'n_intervals')]
)
def update_table(n_clicks, n_intervals):
    data = fetch_experiments_data()
    if data:
        # Convert to DataFrame and return as dict records
        df = pd.DataFrame(data)
        return df.to_dict('records')
    return []


# Run the app
if __name__ == '__main__':
    app.run_server(debug=True)
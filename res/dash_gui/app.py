import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import dash_table
import requests
import pandas as pd
import dash_bootstrap_components as dbc

# Initialize the Dash app with a Bootstrap theme
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.CYBORG])

# Define the layout of the app
app.layout = dbc.Container(
    [
        dbc.Row(
            dbc.Col(
                html.H1(
                    "Experiments Dashboard",
                    className="text-center text-primary mb-4"
                ),
                width=12
            )
        ),
        dbc.Row(
            dbc.Col(
                dbc.Button(
                    "Refresh Data",
                    id="refresh-button",
                    n_clicks=0,
                    color="primary",
                    className="mb-4"
                ),
                width={"size": 2, "offset": 5},  # Centering the button
                className="d-grid gap-2"
            )
        ),
        dbc.Row(
            dbc.Col(
                dash_table.DataTable(
                    id='experiments-table',
                    columns=[{"name": i, "id": i} for i in ['id', 'name', 'description']],
                    data=[],  # Initially empty
                    style_table={'overflowX': 'auto'},
                    style_cell={
                        'textAlign': 'left',
                        'padding': '10px',
                        'backgroundColor': '#2A2A2A',  # Table background color
                        'color': 'white'  # Text color
                    },
                    style_header={
                        'backgroundColor': 'black',
                        'fontWeight': 'bold'
                    },
                    style_data_conditional=[
                        {
                            'if': {'row_index': 'odd'},
                            'backgroundColor': '#323232'
                        }
                    ],
                    page_size=10,  # Show only 10 rows per page
                ),
                width=12
            )
        ),
        # Hidden div to hold refresh interval
        dcc.Interval(
            id='interval-component',
            interval=10 * 1000,  # Refresh every 10 seconds
            n_intervals=0
        )
    ],
    fluid=True,  # Make the container fluid for responsiveness
    className="p-4"  # Padding around the entire app
)

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
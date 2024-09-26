import json
import threading
import websocket
import dash
import dash_bootstrap_components as dbc
import dash_table
import pandas as pd
from communication.experiments import fetch_experiments_data
from dash import dcc, html
from dash.dependencies import Input, Output, State

# Initialize the Dash app with a Bootstrap theme
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.CYBORG])
global ws_messages
ws_messages = []  # Clear the global message log after displaying


# Define the layout of the app
app.layout = dbc.Container(
    [
        dbc.Row(
            dbc.Col(
                html.H1(
                    "Experiments Dashboard", className="text-center text-primary mb-4"
                ),
                width=12,
            )
        ),
        dbc.Row(
            dbc.Col(
                dbc.Button(
                    "Refresh Data",
                    id="refresh-button",
                    n_clicks=0,
                    color="primary",
                    className="mb-4",
                ),
                width={"size": 2, "offset": 5},  # Centering the button
                className="d-grid gap-2",
            )
        ),
        dbc.Row(
            dbc.Col(
                dash_table.DataTable(
                    id="experiments-table",
                    columns=[{"name": i, "id": i} for i in ["id", "type"]],
                    data=[],  # Initially empty
                    style_table={"overflowX": "auto"},
                    style_cell={
                        "textAlign": "left",
                        "padding": "10px",
                        "backgroundColor": "#2A2A2A",  # Table background color
                        "color": "white",  # Text color
                    },
                    style_header={"backgroundColor": "black", "fontWeight": "bold"},
                    style_data_conditional=[
                        {"if": {"row_index": "odd"}, "backgroundColor": "#323232"}
                    ],
                    page_size=10,  # Show only 10 rows per page
                ),
                width=12,
            )
        ),
        dbc.Row(
            dbc.Col(
                html.Div(
                    id="websocket-events",
                    className="mt-4",
                    style={"whiteSpace": "pre-line", "color": "lime"},
                ),
                width=12,
            )
        ),
        # Hidden div to hold refresh interval
        dcc.Interval(
            id="interval-component",
            interval=10 * 500,  # Refresh every 10 seconds
            n_intervals=0,
        ),
    ],
    fluid=True,  # Make the container fluid for responsiveness
    className="p-4",  # Padding around the entire app
)


# Callback to update the table with new data
@app.callback(
    Output("experiments-table", "data"),
    [Input("refresh-button", "n_clicks"), Input("interval-component", "n_intervals")],
)
def update_table(n_clicks, n_intervals):
    data = fetch_experiments_data()
    if data:
        # Convert to DataFrame and return as dict records
        df = pd.DataFrame(data)
        return df.to_dict("records")
    return []


# WebSocket client handling function
def on_message(ws, message):
    global ws_messages
    ws_messages.append(json.loads(message))
    print(f"WebSocket message received: {message}")


def on_error(ws, error):
    print(f"WebSocket error: {error}")


def on_close(ws, close_status_code, close_msg):
    print(f"WebSocket closed: {close_status_code} - {close_msg}")


def on_open(ws):
    print("WebSocket connection opened")


# Start WebSocket in a separate thread
def start_websocket(experiment_id):
    websocket_url = f"ws://127.0.0.1:8000/experiments/{experiment_id}/events"
    ws = websocket.WebSocketApp(
        websocket_url, on_message=on_message, on_error=on_error, on_close=on_close
    )
    ws.on_open = on_open
    ws.run_forever()


# Callback to handle the selected experiment and start WebSocket connection
@app.callback(
    Output("websocket-events", "children"),
    [
        Input("experiments-table", "active_cell"),
        Input("interval-component", "n_intervals"),
    ],
    [State("websocket-events", "children")],
)
def connect_to_websocket(selected_experiment_id, n_intervals, existing_logs):
    if n_intervals:
        global ws_messages
        new_logs = "\n".join([json.dumps(msg) for msg in ws_messages])
        ws_messages = []  # Clear the global message log after displaying
        return (existing_logs or "") + "\n" + new_logs

    elif selected_experiment_id:
        # Start WebSocket connection in a new thread
        ws_thread = threading.Thread(
            target=start_websocket, args=(selected_experiment_id["row_id"],)
        )
        ws_thread.start()
        return existing_logs or "Listening for WebSocket events..."
    return "Select an experiment to start listening for events."


# Run the app
if __name__ == "__main__":
    app.run_server(debug=True)

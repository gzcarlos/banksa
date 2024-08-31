import dash
from dash import html, dcc, callback, Input, Output, State
import dash_bootstrap_components as dbc
from model.connections import (
    add_folder_to_db, 
    get_current_folder_from_db,
    update_folder_in_db
)


layout = html.Div(
    children=[
        dcc.Location(id='url', refresh=False),
        dbc.Container(
            children=[
                html.H1("Folder Management", className="my-4"),
                dbc.Input(id="folder-input", type="text", placeholder="Enter folder path", className="mb-3"),
                dbc.Button("Add Folder", id="submit-button", color="primary", className="mb-3"),
                html.Div(id="output-message"),
                dbc.Button("Update Folder", id="update-button", color="secondary", className="mb-3", style={'display': 'none'}),
                html.Div(id="output-update-message", children='')
            ],
            id='home-container'
        )
    ]
)

@callback(
    Output("output-message", "children"),
    Input("submit-button", "n_clicks"),
    State("folder-input", "value"),
    prevent_initial_call=True
)
def handle_add_folder(n_clicks, folder_path):
    if not folder_path:
        return "Please enter a folder id."
    
    result = add_folder_to_db(folder_path)
    return result
@callback(
    Output('home-container', 'children'),
    Input("_pages_location", "pathname"),
    suppress_callback_exceptions=True
)
def get_current_folder(pathname):
    current_folder_id, message = get_current_folder_from_db()
    container_children = []
    if current_folder_id is None:
        container_children = [
            html.H1("Folder Management", className="my-4"),
            dbc.Input(id="folder-input", type="text", placeholder="Enter folder path", className="mb-3"),
            dbc.Button("Add Folder", id="submit-button", color="primary", className="mb-3"),
            html.Div(id="output-message", children=message)
        ]
    else:
        container_children = [
            html.H1("Folder Management", className="my-4"),
            dbc.Input(id="folder-input", type="text", placeholder="Enter folder path", className="mb-3", value=current_folder_id),
            dbc.Button("Update Folder", id="update-button", color="secondary", className="mb-3"),
            html.Div(id="output-update-message", children=message)
        ]

    return container_children

@callback(
    Output('output-update-message', 'children'),
    Input('update-button', 'n_clicks'),
    State('folder-input', 'value'),
    prevent_initial_call=True,
    suppress_callback_exceptions=True
)
def update_folder(n_clicks, folder_name):
    if n_clicks:
        if folder_name is not None and len(folder_name) > 1:
            updated_rows, message = update_folder_in_db(folder_name)
            if updated_rows > 0:
                return message
            else:
               return f'Cloud not update the folder id. {message}'

# Register the page
dash.register_page(__name__, path='/', layout=layout, name='Home')
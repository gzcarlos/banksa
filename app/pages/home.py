import dash
from dash import html, dcc, callback, Input, Output, State, dash_table
import dash_bootstrap_components as dbc
import pandas as pd
from model.connections import (
    add_folder_to_db, 
    get_current_folder_from_db,
    update_folder_in_db,
    get_uploaded_files,
)

# @callback(
#     Output('home-container', 'children'),
#     Input("_pages_location", "pathname"),
#     suppress_callback_exceptions=True
# )
# def get_current_folder(pathname):
#     current_folder_id, message = get_current_folder_from_db()
#     container_children = []
#     if current_folder_id is None:
#         container_children = [
#             html.H1("Folder Management", className="my-4"),
#             dbc.Input(id="folder-input", type="text", placeholder="Enter folder path", className="mb-3"),
#             dbc.Button("Add Folder", id="submit-button", color="primary", className="mb-3"),
#             html.Div(id="output-message", children=message)
#         ]
#     else:
#         container_children = [
#             html.H1("Folder Management", className="my-4"),
#             dbc.Input(id="folder-input", type="text", placeholder="Enter folder path", className="mb-3", value=current_folder_id),
#             dbc.Button("Update Folder", id="update-button", color="secondary", className="mb-3"),
#             html.Div(id="output-update-message", children=message)
#         ]

#     return container_children

@callback(
    Output('home-content', 'children'),
    Input("url", "pathname"),
    # suppress_callback_exceptions=True,
    prevent_initial_call=True,
)
def show_files(pathname):
    df, message = get_uploaded_files()

    if df.empty:
        return layout_when_no_data()
    else:
        return layout_when_data(df)

def layout_when_no_data():
    return [
        html.P("You have no files uploaded.", className="mb-3"),
        html.A("Upload One", href="/upload", className="mb-1 btn btn-primary"),
    ]

def get_style_data_conditional():
    return [
        {
            'if': {'column_id' : 'file_size'},
            'textAlign': 'right'
        },
        {
            'if': {'column_id' : 'n_transactions'},
            'textAlign': 'right'
        },
        {
            'if': {'column_id' : 'content_processed'},
            'textAlign': 'center'
        },
        {
            'if': {'column_id' : 'transactions_extracted'},
            'textAlign': 'center'
        },
        {
            'if': {
                'column_id' : 'transactions_extracted',
                'filter_query': '{transactions_extracted} = "Yes"'
            },
            'backgroundColor': '#91FFD5'
        },
        {
            'if': {
                'column_id' : 'transactions_extracted',
                'filter_query': '{transactions_extracted} = "No"'
            },
            'backgroundColor': '#FFA491'
        },
        {
            'if': {
                'column_id' : 'content_processed',
                'filter_query': '{content_processed} = "Yes"'
            },
            'backgroundColor': '#91FFD5'
        },
        {
            'if': {
                'column_id' : 'content_processed',
                'filter_query': '{content_processed} = "No"'
            },
            'backgroundColor': '#FFA491'
        },
    ]

def layout_when_data(df: pd.DataFrame):
    home_content = [
        html.P("This are the files you have uploaded.", className="mb-3"),
        html.A("Upload more", href="/upload", className="mb-3 btn btn-info"),
    ]
    
    style_data_conditional = get_style_data_conditional()

    data_table = dash_table.DataTable(
        id='file-table',
        data=df.to_dict('records'),
        columns=[
            {'name': 'File Name', 'id': 'file_name', "type":"text"},
            {'name': 'Size (bytes)', 'id': 'file_size', "type":"numeric", "format": dash_table.Format.Format(precision=2, scheme=dash_table.Format.Scheme.fixed)},
            {'name': 'Content Processed?', 'id': 'content_processed', "type":"text"},
            {'name': 'Transactions Extracted?', 'id': 'transactions_extracted', "type":"text"},
            {'name': '# Transactions', 'id': 'n_transactions', "type":"numeric"}
        ],
        style_table={'height': '400px', 'overflowY': 'auto'},
        style_cell={'textAlign': 'left'},
        style_header={
            'backgroundColor': 'rgb(230, 230, 230)',
            'fontWeight': 'bold'
        },
        style_data_conditional=style_data_conditional,
        sort_action='native',
        filter_action='native',
    )

    home_content.append(data_table)

    return home_content

layout = html.Div(
    children=[
        dcc.Location(id='url', refresh=False),
        dbc.Container(
            children=[
                html.H1("Files", className="my-4"),
                html.Div(
                    children=layout_when_no_data(),
                    id='home-content'
                ),
                # dbc.Input(id="folder-input", type="text", placeholder="Enter folder path", className="mb-3"),
                # dbc.Button("Add Folder", id="submit-button", color="primary", className="mb-3"),
                # html.Div(id="output-message"),
            ],
            id='home-container'
        )
    ]
)

# Register the page
dash.register_page(__name__, path='/', layout=layout, name='Home')
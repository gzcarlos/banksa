import dash
from dash import html, dcc, callback, Input, Output, State, dash_table
import dash_bootstrap_components as dbc
import pandas as pd
from model.connections import (
    get_file_transactions,
    get_uploaded_files,
)

@callback(
    Output('trans-file-select', 'options'),
    Output('trans-file-select', 'value'),
    Input("url", "pathname"),
    # suppress_callback_exceptions=True,
    # prevent_initial_call=True,
)
def update_file_list(pathname):
    df, message = get_uploaded_files()

    options = [
        {
            'label': f'{row["file_name"]} ({row["file_size"]} KB)',
            'value': row["id"]
        } 
        for index, row in df.iterrows()
    ]
    value = df[(df['id'] == df['id'].max())]['id'][0]
    return options, value

@callback(
    Output('trans-data', 'data'),
    Output('trans-data', 'columns'),
    Output('trans-data', 'style_data_conditional'),
    Input('trans-file-select', 'value'),
)
def update_table(file_id):
    df, message = get_file_transactions(file_id)

    # df['type'] = df['type'].astype(str).str.title

    columns = [
        {'name': 'ID', 'id': 'id', 'type': 'text'},
        # {'name': 'Statement Date', 'id': 'statement_date', 'type': 'datetime'},
        {'name': 'Trans. Date', 'id': 'date', 'type': 'datetime'},
        {'name': 'Description', 'id': 'description', 'type': 'text'},
        {'name': 'Category', 'id': 'category', 'type': 'text'},
        {'name': 'Amount', 'id': 'amount', 'type': 'numeric', "format": dash_table.Format.Format(precision=2, scheme=dash_table.Format.Scheme.fixed)},
        {'name': 'Currency', 'id': 'currency', 'type': 'text'},
        {'name': 'Type', 'id': 'type', 'type': 'text'},
    ]

    style_data_conditional = [
        {
            'if': {
                'column_id': 'id'
            },
            'textAlign': 'center'
        },
        {
            'if': {
                'column_id': 'amount'
            },
            'textAlign': 'right'
        },
        {
            'if': {
                'filter_query': '{type} = "debit"',
                'column_id': 'type'
            },
            'backgroundColor': '#FFA491',
            'textAlign': 'center'
        },
        {
            'if': {
                'filter_query': '{type} = "credit"',
                'column_id': 'type'
            },
            'backgroundColor': '#91FFD5',
            'textAlign': 'center'
        },
    ]

    return df.to_dict('records'), columns, style_data_conditional

def get_style_data_conditional():
    return None


layout = html.Div(
    children=[
        dcc.Location(id='url', refresh=False),
        dbc.Container(
            children=[
                html.H1("Transactions", className="my-4"),
                html.Div(
                    children=[
                        dbc.Select(
                            id='trans-file-select',
                            className='mb-3'
                        ),
                        dash_table.DataTable(
                            id='trans-data',
                            style_table={'height': '400px', 'overflowY': 'auto'},
                            style_cell={'textAlign': 'left'},
                            style_header={
                                'backgroundColor': 'rgb(230, 230, 230)',
                                'fontWeight': 'bold'
                            },
                            sort_action='native',
                            filter_action='native',
                        )
                    ],
                    id='trans-content'
                ),
                # dbc.Input(id="folder-input", type="text", placeholder="Enter folder path", className="mb-3"),
                # dbc.Button("Add Folder", id="submit-button", color="primary", className="mb-3"),
                # html.Div(id="output-message"),
            ],
            id='trans-container'
        )
    ]
)


# Register the page
dash.register_page(__name__, path='/transactions', layout=layout, name='Transactions')
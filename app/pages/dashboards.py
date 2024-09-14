import dash
from dash import html, dcc, callback, Input, Output, State, dash_table
import dash_bootstrap_components as dbc
import pandas as pd
import model.connections as db


def layout():
    return html.Div(
    children=[
        dcc.Location(id='dash-url', refresh=False),
        dbc.Container(
            children=[
                html.H1("Dasboards", className="my-4"),
                html.Div(id='result-message'),
                html.Div(
                    children=[
                        html.P('Here are some valuable information. Filter for "User" or "Administrator" graphs', id='dash-label', className="mb-3"),
                        dbc.Select(
                            id='dash-file-select',
                            options=[
                                {'label': 'for User', 'value': 1},
                                {'label': 'for Administrator', 'value': 2},
                            ],
                            value=1,
                            className='mb-3 w-25'
                        ),
                        html.Div(id='dash-inner-content'),
                    ],
                    id='dash-content'
                ),
            ],
            id='dash-container'
        ),
    ]
)

def inner_layout_user():
    return None

def inner_layout_admin():
    return None

@callback(
    Output('dash-inner-content', 'children'),
    Input('dash-file-select', 'value'),
)
def update_layout(value):
    if int(value) == 1:
        return inner_layout_user()
    elif int(value) == 2:
        return inner_layout_admin()



# Register the page
dash.register_page(__name__, path='/dashboards', layout=layout(), name='Dashboards')
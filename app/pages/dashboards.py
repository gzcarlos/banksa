import dash
from dash import html, dcc, callback, Input, Output, State, dash_table
import plotly.express as px
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
    df_files, mes1 = db.get_uploaded_files()
    
    if df_files.empty:
        return no_data_layout()

    
    df_all_trans = pd.DataFrame()
    for i, row in df_files.iterrows():
        df_trans, mes2 = db.get_file_transactions(row['id'])
        df_all_trans = pd.concat([df_trans, df_all_trans], ignore_index=True)

    df_overall_grouped = df_all_trans.groupby('category', as_index=False).agg({'amount': 'sum', 'id': 'count'})
    df_overall_grouped.columns = ['category', 'amount', 'count']

    fig_overall_amount = px.pie(df_overall_grouped, values='amount', names='category', title='Categories By Amount', height=600, hole=.3)
    fig_overall_count = px.pie(df_overall_grouped, values='count', names='category', title='Categories By Amount', height=600, hole=.3)
    return html.Div([
                html.H4('Overall Transactions Consumption', className='mb-3'),
                dcc.Graph(id='overall-categories-amount', className='mb-3', figure=fig_overall_amount),
                dcc.Graph(id='overall-categories-count', className='mb-3', figure=fig_overall_count),
            ],
            className='mt-2'
        )

def inner_layout_admin():
    return None

def no_data_layout():
    return html.Div(html.H5('There is no data at the moment.'))


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
import dash
from dash import html, dcc, callback, Input, Output, State, dash_table
import plotly.express as px
import dash_bootstrap_components as dbc
import pandas as pd
import model.connections as db


def layout():
    df_files, msg = db.get_uploaded_files()

    #initialize options list
    files_options_list = [
        {'label': 'All', 'value': 0},
        
    ] + [
        {
            'label': f"{row['file_name']} ({row['file_size']})", 
            'value': row['id']
        } for i, row in df_files.iterrows()
    ]

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
                            id='dash-user-type-select',
                            options=[
                                {'label': 'for User', 'value': 1},
                                {'label': 'for Administrator', 'value': 2},
                            ],
                            value=1, # 1 = User
                            className='mb-3 w-25'
                        ),
                        dbc.Select(
                            id='dash-files-select',
                            options=files_options_list,
                            value=0, # all
                            className='mb-3 w-50',
                            style={'display': 'none'},
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

def inner_layout_user(file_id):
    df_files, mes1 = db.get_uploaded_files()
    
    if df_files.empty:
        return no_data_layout()

    
    df_all_trans = pd.DataFrame()
    for i, row in df_files.iterrows():
        if int(file_id) == 0 or int(row['id']) == int(file_id): # all
            df_trans, mes2 = db.get_file_transactions(row['id'])
            df_all_trans = pd.concat([df_trans, df_all_trans], ignore_index=True)

    df_overall_grouped = df_all_trans.groupby('category', as_index=False).agg({'amount': 'sum', 'id': 'count'})
    df_overall_grouped.columns = ['category', 'amount', 'count']

    fig_overall_amount = px.pie(df_overall_grouped, values='amount', names='category', title='Categories By Amount', height=600, hole=.3)
    fig_overall_count = px.pie(df_overall_grouped, values='count', names='category', title='Categories By No. Transactions', height=600, hole=.3)
    return html.Div([
                html.H4('Overall Transactions Consumption', className='mb-3'),
                dcc.Graph(id='overall-categories-amount', className='mb-1', figure=fig_overall_amount),
                dcc.Graph(id='overall-categories-count', className='mb-1', figure=fig_overall_count),
            ],
            className='mt-2'
        )

def inner_layout_admin():
    df_kb, mes = db.get_voted_descriptions()
    df_evals, mes2 = db.get_evaluations()

    # set the data for feedbacks
    df_kb['vote'] = df_kb.apply(lambda row: 'downvoted' if row['downvoted'] else 'upvoted', axis=1)

    df_votes = df_kb.groupby('vote', as_index=False).agg({'id': 'count'})
    
    df_votes.columns = ['vote', 'count']

    fig_votes = px.pie(df_votes, values='count', names='vote', title='All Feedback Votes', height=600, hole=.3)

    # set the figure for consine similarity
    fig_similarity = px.line(df_evals, x="created_at", y="cosine_similarity_mean", title='Cosine Similarity (average)')

    # set the figure for hit rate metric
    fig_hitrate = px.line(df_evals, x="created_at", y="hit_rate", title='Hit-Rate evaluation')

    return html.Div([
                html.H4('Overall performance', className='mb-3'),
                dcc.Graph(id='kb-feedbacks', className='mb-1', figure=fig_votes),
                dcc.Graph(id='kb-similarity', className='mb-1', figure=fig_similarity),
                dcc.Graph(id='kb-hitrate', className='mb-1', figure=fig_hitrate),
            ],
            className='mt-2'
        )

def no_data_layout():
    return html.Div(html.H5('There is no data at the moment.'))

def normalize_votes(row):
    if row['upvoted'] == True:
        row['vote'] = 'up'
    else:
        row['vote'] = 'down'
    return row

@callback(
    Output('dash-inner-content', 'children'),
    Output('dash-files-select', 'style'),
    Input('dash-user-type-select', 'value'),
    Input('dash-files-select', 'value',)
)
def update_layout(user_type, file_id):
    style = {}
    if int(user_type) == 1 and int(file_id) >= 0:
        style = {}
        return inner_layout_user(file_id), style
    elif int(user_type) == 2:
        style = {'display': 'none'}
        return inner_layout_admin(), style



# Register the page
dash.register_page(__name__, path='/dashboards', layout=layout(), name='Dashboards')
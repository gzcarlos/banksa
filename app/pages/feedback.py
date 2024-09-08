import dash
from dash import html, dcc, callback, Input, Output, State, dash_table
import dash_bootstrap_components as dbc
import pandas as pd
import model.connections as db


def layout():
    return html.Div(
    children=[
        dcc.Location(id='feed-url', refresh=False),
        dbc.Container(
            children=[
                html.H1("Feedback", className="my-4"),
                html.Div(id='result-message'),
                html.Div(
                    children=[
                        html.P("There are not transactions to give feedback.", id='feed-label', className="mb-3"),
                        dash_table.DataTable(
                            id='feed-data',
                            style_table={'height': '400px', 'overflowY': 'auto'},
                            style_cell={'textAlign': 'left'},
                            style_header={
                                'backgroundColor': 'rgb(230, 230, 230)',
                                'fontWeight': 'bold'
                            },
                            sort_action='native',
                            filter_action='native',
                            # pagination
                            page_action='native',
                            page_current= 0,
                            page_size= 10,
                            # selectable
                            row_selectable='single',
                            selected_rows=[],
                            # className='mb-3',
                        ),
                        html.Hr(className="my-2"),
                        # dbc.Alert(id='alert-sucess', color='success'),
                        # dbc.Alert(id='alert-danger', color='danger'),
                        html.Div( 
                            id='record-detail',
                            className='mb-3'
                        ),
                    ],
                    id='feed-content'
                ),
                # dbc.Input(id="folder-input", type="text", placeholder="Enter folder path", className="mb-3"),
                # dbc.Button("Add Folder", id="submit-button", color="primary", className="mb-3"),
                # html.Div(id="output-message"),
            ],
            id='feed-container'
        ),
    ]
)


@callback(
    Output('feed-label', 'children'),
    Output('feed-data', 'columns'),
    Output('feed-data', 'data'),
    Output('feed-data', 'style_data_conditional'),
    Input("feed-url", "pathname"),
    # suppress_callback_exceptions=True,
    # prevent_initial_call=True,
)
def update_file_list(pathname):
    df, message = db.get_missing_vote_descriptions()

    columns = [
        {'name': 'ID', 'id': 'id', 'type': 'text'},
        {'name': 'Description', 'id': 'description', 'type': 'text'},
        {'name': 'Category', 'id': 'category', 'type': 'text'},
    ]

    style_data_conditional = get_style_data_conditional()
    
    data = None
    
    if not df.empty:
        feed_label = "Select a transaction description to give feedback using the mark on first column."
        data = df.to_dict('records')
    else:
        feed_label = 'There are not transactions to give feedback. Try uploading a new document to get transactions and then new descriptions'
    
    return feed_label, columns, data, style_data_conditional

@callback(
    Output('fade-wrong', 'is_in'),
    Input('btn-wrong', 'n_clicks'),
    State('fade-wrong', 'is_in'),
    prevent_initial_call=True,
)
def toogle_fade_suggestion(n, is_in):
    if not n:
        return False
    return not is_in

@callback(
    Output('result-message', 'children'),
    Input('btn-confirm', 'n_clicks'),
    Input('btn-correct', 'n_clicks'),
    State('input-suggested-cat', 'value'),
    State('record-detail-id', 'children'),
    State('record-detail-desc', 'children'),
    State('record-detail-category', 'children'),
    prevent_initial_call=True,
)
def save_suggested_category(
    n_confirm, 
    n_correct, 
    suggested_value, 
    record_id,
    record_desc,
    record_category
):
    if n_confirm and n_confirm > 0:
        # save feedback
        rows, message = db.save_feedback(
            is_correct=False, 
            id=record_id, 
            desc=record_desc, 
            category=None, 
            suggested_category=suggested_value
        )
        print(f'is_correct=False {rows=}')

        if rows in [0, -1]:
            return dbc.Alert(message, color='danger')
        else:
            return dbc.Alert(f'{suggested_value} category updated as suggested.', color='success')

    elif n_correct and n_correct > 0:
        # save feedback
        rows, message = db.save_feedback(
            is_correct=True, 
            id=record_id, 
            desc=record_desc, 
            category=record_category, 
            suggested_category=None
        )
        print(f'is_correct=True {rows=}')
        
        if rows in [0, -1]:
            return dbc.Alert(message, color='danger')
        else:
            return dbc.Alert(f'{record_category} category confirmed.', color='success')
    
    

@callback(
    # Output('feed-data', 'data'),
    Output('record-detail', 'children'),
    Input('feed-data', 'derived_virtual_data'),
    Input('feed-data', 'derived_virtual_selected_rows'),
    suppress_callback_exceptions=True,
)
def get_row(rows, selected_rows):
    if selected_rows is None:
        selected_rows = []
    
    if len(selected_rows) > 0:
        df = df if rows is None else pd.DataFrame(rows)
        row = df.to_dict('records')[selected_rows[0]]
        children = build_record_detail_layout(row['id'], row['description'], row['category'])
        return children

def get_style_data_conditional():
    return [
        {
            'if': {
                'column_id': 'id'
            },
            'textAlign': 'center'
        },
    ]

def build_record_detail_layout(id, desc, category):
    return [
            html.H1("Is this the right category?", className="display-5 mb-5"),
            dbc.Row([
                dbc.Col(html.Strong('ID'), width=2),
                dbc.Col(html.Div(id, id='record-detail-id'), width=4),
            ]),
            dbc.Row([
                dbc.Col(html.Strong('Description'), width=2),
                dbc.Col(html.Div(desc, id='record-detail-desc'), width=4),
            ]),
            dbc.Row([
                dbc.Col(html.Strong('Category'), width=2),
                dbc.Col(html.Div(category, id='record-detail-category'), width=4),
            ]),
            dbc.Button('Yes', id='btn-correct', color='success', className='me-1 mt-4 mb-3'),
            dbc.Button('No', id='btn-wrong', color='danger', className='me-1 mt-4 mb-3'),
            dbc.Fade(
                html.Div(
                    children=[
                        dbc.FormFloating([
                            dbc.Input(id='input-suggested-cat', type='text', placeholder='CINEMA'),
                            dbc.Label('Suggest a Category here'),
                        ]),
                        dbc.Button('Confirm', id='btn-confirm', color='primary', className='me-1 mt-4'),
                    ]
                ),
                id='fade-wrong', 
                is_in=False, 
                appear=False
            ),
        ]


# Register the page
dash.register_page(__name__, path='/feedback', layout=layout(), name='Feedback')


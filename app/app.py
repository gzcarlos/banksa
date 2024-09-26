import dash
from dash import html, dcc
import dash_bootstrap_components as dbc
import os
import dash_uploader as du
# from pages import home

app = dash.Dash(__name__, use_pages=True, external_stylesheets=[dbc.themes.BOOTSTRAP])

# Set up a folder for file uploads
UPLOAD_FOLDER_ROOT = "uploads"
if not os.path.exists(UPLOAD_FOLDER_ROOT):
    os.makedirs(UPLOAD_FOLDER_ROOT)

# Configure the uploader
du.configure_upload(app, UPLOAD_FOLDER_ROOT)

app.layout = html.Div([
    dbc.NavbarSimple(
        children=[
            dbc.NavItem(dbc.NavLink(f"{page['name'].title()}", href=page['relative_path'])) for page in dash.page_registry.values()
        ] ,
        brand="Bank Statement Analyser",
        brand_href="/",
        color="primary",
        dark=True,
    ),
    dash.page_container
])

if __name__ == '__main__':
    app.run_server(debug=True, host='0.0.0.0')
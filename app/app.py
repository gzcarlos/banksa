import dash
from dash import html, dcc
import dash_bootstrap_components as dbc
# from pages import home

app = dash.Dash(__name__, use_pages=True, external_stylesheets=[dbc.themes.BOOTSTRAP])

app.layout = html.Div([
    dbc.NavbarSimple(
        children=[
            dbc.NavItem(dbc.NavLink(f"{page['name'].title()}", href=page['relative_path'])) for page in dash.page_registry.values()
        ] ,
        brand="Bank Statement Appreciator",
        brand_href="/",
        color="primary",
        dark=True,
    ),
    dash.page_container
])

if __name__ == '__main__':
    app.run_server(debug=True)
import dash
import dash_bootstrap_components as dbc
from dash import Dash, html, Output, Input, dcc

app = dash.Dash(__name__, use_pages=True, external_stylesheets=[dbc.themes.SPACELAB, dbc.icons.BOOTSTRAP])
server = app.server

magenta = '#db0f72'

# the style arguments for the sidebar. We use position:fixed and a fixed width
SIDEBAR_STYLE = {
    "position": "fixed",
    "top": 0,
    "left": 0,
    "bottom": 0,
    "width": "13rem",
    "padding": "2rem 1rem",
    "background-color": magenta #"#f8f9fa",
}

# the styles for the main content position it to the right of the sidebar and
# add some padding.
CONTENT_STYLE = {
    "margin-left": "10rem",
    #"margin-right": '5rem',
    #'padding': '2rem'
    #'margin-right': '10%',
    "margin-top": "2em"
}

sidebar = html.Div([
    dbc.Card([
        dbc.CardImg(src='assets/logo.png', style={'margin-top': '5px'})
        ], style={'width': '8rem', 'height': '5rem', 'margin-left': '18px'}),
    html.Br(),
    html.Div(['Created By', html.Br()], style={'height': '1px', 'font-size':'13px', 'color':'white'}),
    html.Br(),
    html.A(children=[html.Div(['Natcha Phonkamhaeng'])], 
        href='https://natcha-p-resume.onrender.com/', 
        title='About Me',
        target='_blank',
        style={'height': '1px', 'font-size':'15px', 'color':'white'}),
    html.Hr(
        style={
            "borderWidth": "0.3vh",
            "width": "100%",
            "borderColor": "#3294a8",
            "opacity": "unset",
        }
        ),
    dbc.Nav([
        dbc.NavLink([
            html.Div(page['name'], className='ms-2 text-white')
            ],
            href=page['path'],
            active='exact',
            )
            for page in dash.page_registry.values()
        ], 
        vertical=True, pills=True),
    ])

app.layout = dbc.Container([
    dbc.Row([
        dbc.Col([
            sidebar
            ],
            style=SIDEBAR_STYLE),
        dbc.Col([
            dash.page_container
            ],
            style=CONTENT_STYLE, width={'size':12})
        ])
    ])


if __name__ == '__main__':
    app.run_server(debug=True)
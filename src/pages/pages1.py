import dash
import dash_bootstrap_components as dbc
from dash import Dash, html, Output, Input, dcc, State, callback
import plotly.express as px
import pandas as pd
import base64
import io

dash.register_page(__name__, path='/', name='Overdue', order=1)

layout = html.Div([
	dcc.Upload(
        id='upload-data',
        children=html.Div([
            'Drag and Drop or ',
            html.A('Select Files')
        ]),
        style={
            'width': '90%',
            'height': '60px',
            'lineHeight': '60px',
            'borderWidth': '1px',
            'borderStyle': 'dashed',
            'borderRadius': '5px',
            'textAlign': 'center',
        },
        # Allow multiple files to be uploaded
        multiple=True
    ),
    html.Div(id='output-data-upload', children=[]),
	])


@callback(
		Output('output-data-upload', 'children'),
		Input('upload-data', 'contents'),
		State('upload-data', 'filename'),
		State('upload-data', 'last_modified'),
		State('output-data-upload', 'children'),
		prevent_initial_call=True
)
def update_output(contents, filename, date, children):
    # part of the code snippet is from https://dash.plotly.com/dash-core-components/upload
    if contents is not None:
        for i, (c, n, d) in enumerate(zip(contents, filename, date)):
            content_type, content_string = contents[i].split(',')
            decoded = base64.b64decode(content_string)

            try:
                if 'xlsx' in filename[i]:
                    # Assume that the user uploaded an excel file
                    df = pd.read_excel(io.BytesIO(decoded))
                    print(df)
            except Exception as e:
                print(e)
                return html.Div([
                    'There was an error processing this file.'
                ])

    
    
import dash
import dash_bootstrap_components as dbc
from dash import Dash, html, Output, Input, dcc, State, callback
import dash_ag_grid as dag
import plotly.express as px
import pandas as pd
import base64
import io

dash.register_page(__name__, path='/', name='Overdue', order=1)

def ag_grid(data):
  # make ag_grid table from df_group_day
  df_pivot = data.pivot(index='Over Due Days', columns='As of', values='Sum of Outstanding').reset_index()
  df_pivot.fillna(0, inplace=True)
  df_pivot.loc['total'] = df_pivot.iloc[:].sum()[1:]
  df_pivot['Over Due Days'].fillna('Total', inplace=True)
  df_pivot.rename(columns={
      'Aging Sort':'Over Due Days',
  }, inplace=True)
  df_pivot['variance'] = df_pivot[df_pivot.columns[2]] - df_pivot[df_pivot.columns[1]]
  df_pivot['% change'] = (df_pivot[df_pivot.columns[3]] / df_pivot[df_pivot.columns[1]]) * 100

  return df_pivot

def title_date(data):
  # date tilte in visualize
  title_date = data['As of'].iloc[-1]
  year, month, date = title_date.split('-')
  return year, month, date


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
                    # data prep
                    df['As of'] = df['As of'].astype('str')
                    df_group_day = df.groupby(['As of', 'Aging Sort'])[['Sum of Outstanding']].sum().reset_index()
                    df_group_day.rename(columns={
                                        'Aging Sort': 'Over Due Days',
                                        }, inplace=True)
                    # plotly graph
                    fig = px.line(df_group_day, \
                    x='Over Due Days', y='Sum of Outstanding', \
                    color='As of', \
                    text='Sum of Outstanding', \
                    title=f'Outstanding Report as of {title_date(df)[2]} - {title_date(df)[1]} - {title_date(df)[0]}')
                    fig.update_traces(textposition="bottom right", texttemplate='%{text:.2s}')

                # creating dashboard after upload data
                dcc.Loading(children=[
                    children.append(dbc.Container([
                    html.Br(),
                    dbc.Row([
                        dbc.Col([
                            dcc.Loading(children=[dcc.Graph(figure=fig)])
                            ])
                        ]),
                    dbc.Row([
                        dbc.Col([
                            dcc.Loading(children=[
                                dag.AgGrid(
                                    rowData = ag_grid(df_group_day).to_dict('records'),
                                    columnDefs = [
                                        {'field': 'Over Due Days', 'width': 150},
                                        {'field': ag_grid(df_group_day).columns[1], 'width': 150, 'type': 'rightAligned', "valueFormatter": {"function": 'd3.format("(,.2f")(params.value)'}},
                                        {'field': ag_grid(df_group_day).columns[2], 'width': 150, 'type': 'rightAligned', "valueFormatter": {"function": 'd3.format("(,.2f")(params.value)'}},
                                        {'field': 'variance', 'width': 150, 'type': 'rightAligned', "valueFormatter": {"function": 'd3.format("(,.2f")(params.value)'}},
                                        {'field': '% change', 'width': 150, 'type': 'rightAligned', "valueFormatter": {"function": 'd3.format("(,.2f")(params.value) + "%"'}},
                                        ],
                                    defaultColDef={"resizable": True, "sortable": True, "filter": True},
                                    columnSize="responsiveSizeToFit",
                                    dashGridOptions={"pagination": True, "paginationPageSize":6, "domLayout": "autoHeight"},
                                    )
                                ])
                            ])
                        ])
                    ])
                )
            ])

                return children

            except Exception as e:
                print(e)
                return html.Div([
                    'There was an error processing this file.'
                ])
    else:
        return ""

    
    
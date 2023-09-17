import dash
import dash_bootstrap_components as dbc
from dash import Dash, html, Output, Input, dcc, State, callback
import dash_ag_grid as dag
import plotly.express as px
import pandas as pd
import base64
import io

dash.register_page(__name__, path='/page-2', name='Root Cause', order=2)

def title_date(data):
  # date tilte in visualize
  title_date = data['As of'].iloc[-1]
  year, month, date = title_date.split('-')
  return year, month, date

def bar_graph(data):
	fig = px.histogram(data, x='Root Cause', y='Sum of Outstanding',\
                   color='As of', barmode='group', text_auto='.2s')
	return fig

def donut_graph(data):
	fig = px.pie(data[data['As of'] == data['As of'].iloc[-1]], \
	             values='Sum of Outstanding', \
	             names='Root Cause',\
	             hole=.3,\
	             title=f'{title_date(data)[2]}-{title_date(data)[1]}-{title_date(data)[0]} Root Cause')
	fig.update_traces(textposition='outside', textinfo='percent+label')
	fig.update(layout_showlegend=False)
	return fig

layout = html.Div([
	dcc.Upload(
        id='upload-data-rootcause',
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
    html.Div(id='output-data-upload-rootcause', children=[]),
	])


@callback(
		Output('output-data-upload-rootcause', 'children'),
		Input('upload-data-rootcause', 'contents'),
		State('upload-data-rootcause', 'filename'),
		State('upload-data-rootcause', 'last_modified'),
		State('output-data-upload-rootcause', 'children'),
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
                    global df_root
                    df = pd.read_excel(io.BytesIO(decoded))
                    df['As of'] = df['As of'].astype('str')
                    df_root_cause = df.groupby(['As of', 'Customer Side / ONE Side'])[['Sum of Outstanding']].sum().reset_index()
                    df_root_cause.rename(columns={
                    	'Customer Side / ONE Side': 'Root Cause',
                    	}, inplace=True)
                    df_root_table = df_root_cause.pivot(index='Root Cause', columns='As of', values='Sum of Outstanding').reset_index()
                    df_root_table.fillna(0, inplace=True)
                    df_root_table['variance'] = df_root_table[df_root_table.columns[1]] - df_root_table[df_root_table.columns[2]]
                    df_root_table['% variance'] = (df_root_table[df_root_table.columns[3]] / df_root_table[df_root_table.columns[1]]) *100
                    df_root = df[df['As of'] == df['As of'].iloc[-1]]
                    df_root = df_root.dropna(subset=['Customer Side / ONE Side'])[['Customer Side / ONE Side', 'Customer Name', 'Sum of Outstanding']]
                    df_root = df_root.groupby(['Customer Side / ONE Side', 'Customer Name'])[['Sum of Outstanding']]\
                    		.sum().sort_values(by='Sum of Outstanding', ascending=False).reset_index()
                
                # creating dashboard after upload data
                dcc.Loading(children=[children.append(
                	dbc.Container([
						dbc.Row([
							dbc.Col([
								dcc.Loading(children=[dcc.Graph(figure=bar_graph(df_root_cause))])
								], width=7),
							dbc.Col([
								dcc.Graph(figure=donut_graph(df_root_cause))
								], width=5)
							]),
						dbc.Row([
							dcc.RadioItems(id={'type':'dynamic-radio'}, options=[x for x in df_root['Customer Side / ONE Side'].unique()], value='Payment Cycle', inline=True, labelStyle= {"margin":"1rem"})
							]),
						dbc.Row([
							dag.AgGrid(
								id={'type': 'dynamic-table'},
					            rowData = df_root.to_dict('records'),
					            columnDefs = [
					                {'field': 'Customer Name', 'width': 150},
					                {'field': 'Sum of Outstanding', 'width': 150, 'type': 'rightAligned', "valueFormatter": {"function": 'd3.format("(,.0f")(params.value)'}},
					                ],
					            defaultColDef={"resizable": True, "sortable": True, "filter": True},
					            columnSize="responsiveSizeToFit",
					            dashGridOptions={"pagination": True, "paginationPageSize":30, "domLayout": "autoHeight"},
					            )
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

@callback(
	Output({'type': 'dynamic-table'}, 'rowData'),
	Input({'type': 'dynamic-radio'}, 'value')
	)
def update_table(select_radio):
	dff = df_root.copy()
	if select_radio == 'Payment Cycle':
		dff = dff[dff['Customer Side / ONE Side'] == 'Payment Cycle']
		return dff.to_dict('records')
	elif select_radio == 'Customer Side':
		dff = dff[dff['Customer Side / ONE Side'] == 'Customer Side']
		return dff.to_dict('records')
	elif select_radio == 'ONE Side':
		dff = dff[dff['Customer Side / ONE Side'] == 'ONE Side']
		return dff.to_dict('records')


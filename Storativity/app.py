# -*- coding: utf-8 -*-

# Run this app with `python app.py` and visit http://127.0.0.1:8050/ in your web browser.
# documentation at https://dash.plotly.com/
# based on ideas at "Dash App With Multiple Inputs" in https://dash.plotly.com/basic-callbacks
# mouse-over or 'hover' behavior is based on https://dash.plotly.com/interactive-graphing
# plotly express line parameters via https://plotly.com/python-api-reference/generated/plotly.express.line.html#plotly.express.line
# Mapmaking code initially learned from https://plotly.com/python/mapbox-layers/.


from flask import Flask
from os import environ

import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import dash_table

import plotly.graph_objects as go
import calculations as calc
import pandas as pd


external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

server = Flask(__name__)
app = dash.Dash(
    server=server,
    url_base_pathname=environ.get('JUPYTERHUB_SERVICE_PREFIX', '/'),
    external_stylesheets=external_stylesheets
)

alpha_df = pd.read_csv('./alpha.csv')
porosity_df = pd.read_csv('./porosity.csv')

app.layout = html.Div([

    html.Div([
        dcc.Markdown('''
            ### EOSC 325: Storativity
            ----------
            '''),
    ], style={'width': '100%', 'display': 'inline-block'}),

    html.Div([
        dcc.Graph(
            id='plot',
        ),

        dcc.Markdown(
            id='Sa_text',
            style={'margin-left': '30px'}
        ),

        html.Div([
            dash_table.DataTable(
                id='alpha_table',
                columns=[{"name": i, "id": i} for i in alpha_df.columns],
                data=alpha_df.to_dict('records'),
                style_cell={'padding': '5px', 'textAlign': 'left', 'backgroundColor': 'Lavender', 'font-family': 'sans-serif'},
                style_header={
                    'backgroundColor': 'CornflowerBlue',
                    'fontWeight': 'bold',
                    'textAlign': 'left',
                    'font-family': 'sans-serif'
                },
            ),
        ], style={'padding': '30px', 'padding-bottom': '0px'} ),

        #styling data tables: https://dash.plotly.com/datatable/style
        html.Div([
            dash_table.DataTable(
                id='porosity_table',
                columns=[{"name": i, "id": i} for i in porosity_df.columns],
                data=porosity_df.to_dict('records'),
                style_cell={'padding': '5px', 'textAlign': 'left', 'backgroundColor': 'Lavender', 'font-family': 'sans-serif'},
                style_header={
                    'backgroundColor': 'CornflowerBlue',
                    'fontWeight': 'bold',
                    'textAlign': 'left',
                    'font-family': 'sans-serif'
                },
            ),
        ], style={'padding': '30px'} ),
    ], style={'width': '70%', 'display': 'inline-block', 'vertical-align': 'middle'}),

    html.Div([
        dcc.Markdown('''
                    **Plot:**
                '''),
        dcc.RadioItems(
            id='y_plotting',
            options=[
                {'label': 'storativity', 'value': 'S'},
                {'label': 'specific storage', 'value': 'Ss'},
                {'label': 'Sw', 'value': 'Sw'}
            ],
            value='S',
            style={'margin-bottom': '30px'}
        ),

        dcc.Markdown('''
            **Alpha (m^2/N):**
        '''),
        dcc.RadioItems(
            id='alpha',
            options=[
                {'label': 'min', 'value': 'min'},
                {'label': 'avg', 'value': 'avg'},
                {'label': 'max', 'value': 'max'}
            ],
            value='avg',
            labelStyle={'display': 'inline-block'},
            style={'margin-bottom': '30px'}
        ),

        dcc.Markdown('''
            **Porosity:**
        '''),
        dcc.RadioItems(
            id='porosity',
            options=[
                {'label': 'min', 'value': 'min'},
                {'label': 'middle', 'value': 'mid'},
                {'label': 'max', 'value': 'max'}
            ],
            value='mid',
            labelStyle={'display': 'inline-block'},
            style={'margin-bottom': '30px'}
        ),

        dcc.Markdown('''
            **Water Density (kg/L):**
        '''),
        dcc.RadioItems(
            id='density',
            options=[
                {'label': 'potable (1.000)', 'value': 'potable'},
                {'label': 'sea water (1.025)', 'value': 'sea_water'},
                {'label': 'brine (1.088)', 'value': 'brine'}
            ],
            value='sea_water',
            style={'margin-bottom': '30px'}
        ),

        dcc.Markdown('''
            **Aquifer Thickness (m):**
        '''),
        dcc.Slider(
            id='thickness',
            min=1,
            max=30,
            step=None,
            marks={
                1: '1',
                2: '2',
                4: '4',
                8: '8',
                15: '15',
                30: '30'
            },
            value=15,
        )
    ], style={'width': '30%', 'display': 'inline-block', 'vertical-align': 'middle'}),


], style={'width': '1000px'})


@app.callback(
    Output(component_id='plot', component_property='figure'),
    Output(component_id='Sa_text', component_property='children'),
    Input(component_id='y_plotting', component_property='value'),
    Input(component_id='alpha', component_property='value'),
    Input(component_id='porosity', component_property='value'),
    Input(component_id='density', component_property='value'),
    Input(component_id='thickness', component_property='value'),
)
def update_plot(y_plotting, inp_alpha, inp_porosity, inp_density, inp_thickness):
    materials = ['Clay', 'Sand', 'Gravel', 'Jointed Rock', 'Sound Rock']

    alpha, porosity, density, thickness = calc.alpha(inp_alpha), calc.porosity(inp_porosity), calc.density(inp_density), inp_thickness

    if y_plotting == 'S':
        y_values = calc.storativity(alpha, porosity, density, thickness)
    elif y_plotting == 'Ss':
        y_values = calc.specific_storage(alpha, porosity, density)
    elif y_plotting == 'Sw':
        y_values = calc.storativity_water_compressibility(porosity, density, thickness)

    fig = go.Figure([go.Bar(x=materials, y=y_values)])
    fig.update_layout(xaxis_title='Material', yaxis_title='Storativity')

    text = 'Storativity due to compressibility of aquifer (Sa): ' + str(calc.storativity_aquifer_compressibility(density))

    return fig, text

if __name__ == '__main__':
    app.run_server(debug=True, host='0.0.0.0', port=8050)

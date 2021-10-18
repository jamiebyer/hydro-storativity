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
from dash import dcc
from dash import html
from dash.dependencies import Input, Output
from dash import dash_table

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

introduction = open('introduction.md', 'r')
introduction_markdown = introduction.read()

sources = open('sources.md', 'r')
sources_markdown = sources.read()

init_y_plotting = 'S'
init_inp_alpha = 'avg'
init_inp_porosity = 'mid'
init_inp_density = 'sea_water'
init_inp_thickness = 15
init_y_axis = 'fitted'


def initialize_plot(y_plotting, inp_alpha, inp_porosity, inp_density, inp_thickness):
    materials = ['Clay', 'Sand', 'Gravel', 'Jointed Rock', 'Sound Rock']

    alpha, porosity, density, thickness = calc.alpha(inp_alpha), calc.porosity(inp_porosity), calc.density(
        inp_density), inp_thickness

    if y_plotting == 'S':
        y_values = calc.storativity(alpha, porosity, density, thickness)
    elif y_plotting == 'Ss':
        y_values = calc.specific_storage(alpha, porosity, density)
    elif y_plotting == 'Sw':
        y_values = calc.storativity_water_compressibility(porosity, density, thickness)

    fig = go.Figure([go.Bar(x=materials, y=y_values)])
    fig.update_layout(xaxis_title='Material')

    if y_plotting == 'S':
        fig.update_layout(xaxis_title='Material', yaxis_title='S (dimensionless)')
    elif y_plotting == 'Ss':
        fig.update_layout(xaxis_title='Material', yaxis_title='Ss (m\u207B\u00B9)')
    elif y_plotting == 'Sw':
        fig.update_layout(xaxis_title='Material', yaxis_title='Sw (dimensionless)')
    fig.update_layout(title='<b>Select parameters, then click "Update Plot."</b>')
    fig.update_layout(title_pad_l=120)

    fig.update_layout(yaxis_type='log', yaxis_range=[-7, 0])
    return fig

fig = initialize_plot(init_y_plotting, init_inp_alpha, init_inp_porosity, init_inp_density, init_inp_thickness)

app.layout = html.Div([

    html.Div([
        dcc.Markdown(
            children=introduction_markdown
        ),
    ], style={'width': '100%', 'display': 'inline-block'}),




    html.Div([
        dcc.Graph(
            id='plot',
            figure=fig
        ),

        dcc.Markdown(
            children='''Water Compressibility (beta) = 4.40E-10 m\u00B2/N.''',
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
                {'label': 'S, storativity', 'value': 'S'},
                {'label': 'Ss, specific storage', 'value': 'Ss'},
                {'label': 'Sw, storativity due to compressibility of water', 'value': 'Sw'}
            ],
            value=init_y_plotting,
            style={'margin-bottom': '30px'}
        ),

        dcc.Markdown('''
            **Alpha (m\u00B2/N):**
        '''),
        dcc.RadioItems(
            id='alpha',
            options=[
                {'label': 'min', 'value': 'min'},
                {'label': 'avg', 'value': 'avg'},
                {'label': 'max', 'value': 'max'}
            ],
            value=init_inp_alpha,
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
            value=init_inp_porosity,
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
            value=init_inp_density,
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
            value=init_inp_thickness,
        ),

        html.Button('Update Plot', id='submit_button', style={'margin-top': '40px', 'margin-bottom': '20px'}),
    ], style={'width': '30%', 'display': 'inline-block', 'vertical-align': 'middle'}),

    dcc.Markdown(
        children=sources_markdown
    ),

], style={'width': '1000px'})



@app.callback(
    Output(component_id='plot', component_property='figure'),
    Input(component_id='submit_button', component_property='n_clicks'),
    Input(component_id='plot', component_property='figure'),
    Input(component_id='y_plotting', component_property='value'),
    Input(component_id='alpha', component_property='value'),
    Input(component_id='porosity', component_property='value'),
    Input(component_id='density', component_property='value'),
    Input(component_id='thickness', component_property='value'),
)
def update_plot(submit_button, og_fig, y_plotting, inp_alpha, inp_porosity, inp_density, inp_thickness):
    if (dash.callback_context.triggered[0]['prop_id'].split('.')[0] == 'submit_button'):
        materials = ['Clay', 'Sand', 'Gravel', 'Jointed Rock', 'Sound Rock']
        alpha, porosity, density, thickness = calc.alpha(inp_alpha), calc.porosity(inp_porosity), calc.density(inp_density), inp_thickness

        if y_plotting == 'S':
            y_values = calc.storativity(alpha, porosity, density, thickness)
        elif y_plotting == 'Ss':
            y_values = calc.specific_storage(alpha, porosity, density)
        elif y_plotting == 'Sw':
            y_values = calc.storativity_water_compressibility(porosity, density, thickness)

        fig = go.Figure([go.Bar(x=materials, y=y_values)])
        fig.update_layout(xaxis_title='Material')

        if y_plotting == 'S':
            fig.update_layout(xaxis_title='Material', yaxis_title='S (dimensionless)')
        elif y_plotting == 'Ss':
            fig.update_layout(xaxis_title='Material', yaxis_title='Ss (m\u207B\u00B9)')
        elif y_plotting == 'Sw':
            fig.update_layout(xaxis_title='Material', yaxis_title='Sw (dimensionless)')
        fig.update_layout(title='<b>Select parameters, then click "Update Plot."</b>')
        fig.update_layout(title_pad_l=120)

        fig.update_layout(yaxis_type='log', yaxis_range=[-7, 0])
        return fig
    else:
        return og_fig

if __name__ == '__main__':
    app.run_server(debug=True, host='0.0.0.0', port=8050)

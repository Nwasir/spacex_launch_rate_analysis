# spacex_dash_app.py

import pandas as pd
import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import plotly.express as px

# Read the SpaceX data into pandas dataframe
spacex_df = pd.read_csv("spacex_launch_dash.csv")

# Get min and max payload for the slider
max_payload = spacex_df['Payload Mass (kg)'].max()
min_payload = spacex_df['Payload Mass (kg)'].min()

# List of launch sites for dropdown
launch_sites = [{'label': 'All Sites', 'value': 'ALL'}] + \
               [{'label': site, 'value': site} for site in spacex_df['Launch Site'].unique()]

# Initialize the Dash app
app = dash.Dash(__name__)

# App layout
app.layout = html.Div(children=[
    html.H1(
        'SpaceX Launch Records Dashboard',
        style={'textAlign': 'center', 'color': '#503D36', 'font-size': 40}
    ),

    # TASK 1: Dropdown for Launch Site selection
    html.Div([
        html.Label("Select Launch Site:"),
        dcc.Dropdown(
            id='site-dropdown',
            options=launch_sites,
            value='ALL',
            placeholder="Select a Launch Site",
            searchable=True,
            style={'width': '80%', 'margin': 'auto'}
        )
    ]),
    html.Br(),

    # TASK 2: Pie chart for launch success
    dcc.Graph(id='success-pie-chart'),
    html.Br(),

    html.P("Payload range (Kg):"),

    # TASK 3: Payload slider
    dcc.RangeSlider(
        id='payload-slider',
        min=0,
        max=10000,
        step=1000,
        marks={
            0: '0',
            2000: '2000',
            4000: '4000',
            6000: '6000',
            8000: '8000',
            10000: '10000'
        },
        value=[min_payload, max_payload]
    ),
    html.Br(),

    # TASK 4: Scatter chart for payload vs. launch success
    dcc.Graph(id='success-payload-scatter-chart'),
])

# TASK 2: Callback for pie chart
@app.callback(
    Output(component_id='success-pie-chart', component_property='figure'),
    Input(component_id='site-dropdown', component_property='value')
)
def get_pie_chart(entered_site):
    if entered_site == 'ALL':
        success_counts = spacex_df[spacex_df['class'] == 1]['Launch Site'].value_counts().reset_index()
        success_counts.columns = ['Launch Site', 'Success Count']
        fig = px.pie(
            success_counts,
            values='Success Count',
            names='Launch Site',
            title='Total Successful Launches by Site'
        )
        return fig
    else:
        filtered_df = spacex_df[spacex_df['Launch Site'] == entered_site]
        outcome_counts = filtered_df['class'].value_counts().reset_index()
        outcome_counts.columns = ['Outcome', 'Count']
        outcome_counts['Outcome'] = outcome_counts['Outcome'].replace({1: 'Success', 0: 'Failure'})
        fig = px.pie(
            outcome_counts,
            values='Count',
            names='Outcome',
            title=f'Success vs. Failure for site {entered_site}'
        )
        return fig

# TASK 4: Callback for scatter chart
@app.callback(
    Output(component_id='success-payload-scatter-chart', component_property='figure'),
    [
        Input(component_id='site-dropdown', component_property='value'),
        Input(component_id='payload-slider', component_property='value')
    ]
)
def get_scatter_plot(entered_site, payload_range):
    low, high = payload_range
    filtered_df = spacex_df[(spacex_df['Payload Mass (kg)'] >= low) &
                             (spacex_df['Payload Mass (kg)'] <= high)]
    
    if entered_site == 'ALL':
        fig = px.scatter(
            filtered_df,
            x='Payload Mass (kg)',
            y='class',
            color='Booster Version Category',
            title='Payload vs. Outcome for All Sites',
            labels={'class': 'Launch Outcome'}
        )
        return fig
    else:
        site_df = filtered_df[filtered_df['Launch Site'] == entered_site]
        fig = px.scatter(
            site_df,
            x='Payload Mass (kg)',
            y='class',
            color='Booster Version Category',
            title=f'Payload vs. Outcome for {entered_site}',
            labels={'class': 'Launch Outcome'}
        )
        return fig

# Run the app
if __name__ == '__main__':
    app.run()

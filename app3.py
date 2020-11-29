import os
import datetime
import requests

import dash
import dash_table
import dash_core_components as dcc
import dash_bootstrap_components as dbc
import plotly.graph_objs as go
from dash.dependencies import Input, Output
import pandas as pd

import tkinter as tk
from PIL import Image, ImageTk
import time
import sys

import mysql.connector as mysql

import dash_html_components as html
import plotly.express as px
import plotly 

from urllib.request import Request, urlopen
from bs4 import BeautifulSoup
import re

from pyorbital.orbital import Orbital

satellite = Orbital('TERRA')


external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(external_stylesheets=[dbc.themes.BOOTSTRAP])

server = app.server
df = px.data.iris() # iris is a pandas DataFrame
fig = px.scatter(df, x="sepal_width", y="sepal_length")
fig2 = go.Figure(data=[go.Scatter(x=[1, 2, 3], y=[4, 1, 2])])
df247 = pd.DataFrame()


app.layout = html.Div([
    html.Div(id='display-value'),
    html.Div(
    [
        dbc.Row(
            [
                dbc.Col(html.Div([
    # represents the URL bar, doesn't render anything
    dcc.Location(id='url', refresh=False),

    # content will be rendered in this element
    html.Div(id='page-content')
]), width="1"),
                dbc.Col(html.Div(dcc.Graph(figure=fig)), width="3"),
                dbc.Col(html.Div([
                    dcc.Graph(id='scatter'),
                    dash_table.DataTable(id='data-table2')
                ]), width="3"),
                dbc.Col(html.Div(
    html.Div([
        html.H4('TERRA Satellite Live Feed'),
        html.Div(id='live-update-text'),
        dcc.Graph(id='live-update-graph'),
        html.Section(id="slideshow", children=[
    html.Div(id="slideshow-container", children=[
        html.Div(id="image"),
        dcc.Interval(id='interval', interval=3000)
    ])
]),
        dash_table.DataTable(id='data-table'),
        dcc.Interval(
            id='interval-component',
            interval=1*1000,  # in milliseconds
            n_intervals=0
        )
    ])), width="4"),
            ]
        ),

    ]
),



])

if __name__ == "__main__":
    app.run_server()

@app.callback(Output('image', 'children'),
              [Input('interval', 'n_intervals')])
def display_image(n):
    
    imagesurl = ["https://i.pinimg.com/originals/af/8d/63/af8d63a477078732b79ff9d9fc60873f.jpg", "https://images.pexels.com/photos/255379/pexels-photo-255379.jpeg?auto=compress&cs=tinysrgb&dpr=1&w=500"]
    for i in imagesurl:
        if n == None or n % 3 == 1:
            img = html.Img(src=i)
        elif n % 3 == 2:
            img = html.Img(src="http://placeimg.com/625/225/animals")
        elif n % 3 == 0:
            img = html.Img(src="http://placeimg.com/625/225/arch")
        else:
            img = "None"
    return img

@app.callback(Output('live-update-text', 'children'),
              [Input('interval-component', 'n_intervals')])

def update_metrics(n):
    lon, lat, alt = satellite.get_lonlatalt(datetime.datetime.now())
    style = {'padding': '5px', 'fontSize': '16px'}
    return [
        html.Span('Longitude: {0:.2f}'.format(lon), style=style),
        html.Span('Latitude: {0:.2f}'.format(lat), style=style),
        html.Span('Altitude: {0:0.2f}'.format(alt), style=style)
    ]

@app.callback([Output('data-table2', 'columns')])
def update_datatable2(n):
    pages247 = ('politiki/','koinonia/','oikonomia/','kosmos/')
    df247 = pd.DataFrame()
    for page in pages247:
        URL="https://www.news247.gr/" + str(page)

        r1 = requests.get(URL)
        coverpage = r1.content
        soup1 = BeautifulSoup(coverpage, 'html.parser')
        coverpage_news = soup1.find_all('h3', class_='article__title bold')
        coverpage_news_text = soup1.find_all('p', class_='article__leadtext')
        coverpage_news_time = soup1.find_all('time')
        coverpage_news_image = soup1.find_all('img', {'src':re.compile('.jpg')})

        coverpage_news = [i.text for i in coverpage_news]

        column_names = ["title", "text", "time", "image"]

        S = pd.DataFrame(list(zip(coverpage_news, coverpage_news_text, coverpage_news_time, coverpage_news_image)), columns =column_names).astype(str)
        df247 = df247.append(S)

    df247 = df247.replace(r'\n',' ', regex=True) 
    df247 = df247.replace(r'\s+', ' ', regex=True)
    df247 = df247.replace(r"^\['|'\]$","", regex=True)
    df247['time']=df247['time'].str.extract(r'(\d{4}-\d{2}-\d{2} \d{2}:\d{2})')

    df247['title'] = df247['title'].astype(str)
    df247['text'] = df247['text'].astype(str)
    df247['time'] = df247['time'].astype(str)

    df247['text'] = df247['text'].replace('<p class="article__leadtext">', '', regex=True)
    df247['text'] = df247['text'].replace('</p>', '', regex=True)

    df247['time']= pd.to_datetime(df247['time'])
    df247 = df247.reset_index(drop=True)
    return df247.to_dict('scrape')

# Multiple components can update everytime interval gets fired.
@app.callback([Output('data-table', 'columns'), Output('data-table', 'data'), Output('scatter', 'figure')],
              [Input('interval-component', 'n_intervals')])
def update_datatable(n):
    data = {
        'time': [],
        'Latitude': [],
        'Longitude': [],
        'Altitude': []
    }
 
    # Collect some data
    for i in range(180):
        time = datetime.datetime.now() - datetime.timedelta(seconds=i*20)
        lon, lat, alt = satellite.get_lonlatalt(
            time
        )
        data['Longitude'].append(lon)
        data['Latitude'].append(lat)
        data['Altitude'].append(alt)
        data['time'].append(time)
 
    df = pd.DataFrame(data={
        "Latitude": data['Latitude'],
        "Longitude": data['Longitude'],
        "Altitude": data['Altitude']
    })


    fig = px.scatter(df, x="Latitude", y="Longitude")

 
    return [{"name": col, "id": col} for col in df.columns], df.to_dict('records'), fig
        
@app.callback(Output('live-update-graph', 'figure'),
              [Input('interval-component', 'n_intervals')])
def update_graph_live(n):
    satellite = Orbital('TERRA')
    data = {
        'time': [],
        'Latitude': [],
        'Longitude': [],
        'Altitude': []
    }

    # Collect some data
    for i in range(180):
        time = datetime.datetime.now() - datetime.timedelta(seconds=i*20)
        lon, lat, alt = satellite.get_lonlatalt(
            time
        )
        data['Longitude'].append(lon)
        data['Latitude'].append(lat)
        data['Altitude'].append(alt)
        data['time'].append(time)

    # Create the graph with subplots
    fig = plotly.tools.make_subplots(rows=2, cols=1, vertical_spacing=0.2)
    fig['layout']['margin'] = {
        'l': 30, 'r': 10, 'b': 30, 't': 10
    }
    fig['layout']['legend'] = {'x': 0, 'y': 1, 'xanchor': 'left'}

    fig.append_trace({
        'x': data['time'],
        'y': data['Altitude'],
        'name': 'Altitude',
        'mode': 'lines+markers',
        'type': 'scatter'
    }, 1, 1)
    fig.append_trace({
        'x': data['Longitude'],
        'y': data['Latitude'],
        'text': data['time'],
        'name': 'Longitude vs Latitude',
        'mode': 'lines+markers',
        'type': 'scatter'
    }, 2, 1)

    return fig
    
@app.callback(dash.dependencies.Output('display-value', 'children'),
              [dash.dependencies.Input('dropdown', 'value')])
def display_value(value):
    return 'You have selected "{}"'.format(value)



if __name__ == '__main__':
    app.run_server(debug=True)
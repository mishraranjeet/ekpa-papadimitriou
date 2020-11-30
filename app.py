import dash
from dash.dependencies import Output, Input
import dash_core_components as dcc
import dash_html_components as html
import requests
from bs4 import BeautifulSoup
import plotly
import plotly.graph_objs as go
from collections import deque
from crawldash import crawl247
from crawldash import crawlcapital
from crawldash import crawliefimerida
from crawldash import crawlbeast
from crawldash import vectorization
import plotly.express as px
import matplotlib.pyplot as plt

import dash_table as dt
import dash_bootstrap_components as dbc
import pandas as pd

import nltk
nltk.download('stopwords')
from nltk.corpus import stopwords
greek_stopwords = stopwords.words('greek')

agent = {"User-Agent":'Mozilla/5.0 (Windows NT 6.3; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/59.0.3071.115 Safari/537.36'}

df247 = crawl247()
capital = crawlcapital()
iefimerida = crawliefimerida()
newsbeast = crawlbeast()

frontDf1= vectorization(df247, capital, iefimerida)

yValue = frontDf1['3let'].value_counts()
xValue = frontDf1['country'].value_counts()
countriesUnique = frontDf1['country'].unique()

fig2 = px.bar(x=xValue.index, y=yValue, template="plotly_dark")
fig2.update_layout(yaxis_visible=False, margin=dict(l=0,r=0,b=0,t=0,pad=0),height=300,paper_bgcolor='#2e3859',plot_bgcolor='#2e3859')

colorscale = ["#deebf7", "#d2e3f3", "#c6dbef", "#b3d2e9", "#9ecae1",
    "#85bcdb", "#6baed6", "#57a0ce", "#4292c6", "#3082be", "#2171b5", "#1361a9",
    "#08519c", "#0b4083", "#08306b"
]

data = dict(
        type = 'choropleth',
        locations = yValue.index,
        colorscale= colorscale,
        z = yValue,
        text = yValue.index,
      )

layout = dict(
    geo = dict(
        showframe = False,
        countrycolor = '#1d2339',
        showocean=True, oceancolor="#2e3859",
        coastlinecolor='#2e3859',
        landcolor = '#7999fe',
        projection = {'type':'mercator'}

    )
)

fig = go.Figure(data = [data],layout = layout)
fig.update_geos(fitbounds="locations")
fig.update_layout(template="plotly_dark",margin=dict(l=0,r=0,b=0,t=0,pad=0),height=300,coloraxis_showscale=False,paper_bgcolor='#2e3859',plot_bgcolor='#2e3859')

app = dash.Dash(__name__,external_stylesheets=[dbc.themes.DARKLY])

server = app.server

SIDEBAR_STYLE = {
    'position': 'fixed',
    'top': 0,
    'left': 0,
    'bottom': 0,
    'width': '16%',
    'padding': '20px 10px',
    'background-color': '#2e3859'
}

CONTENT_STYLE = {
    'margin-left': '18%',
    'margin-right': '2%',
    'padding': '20px 10p',
}

CARD_TEXT_STYLE = {
    'textAlign': 'center',
    'color': '#2e3859'
}

controls = dbc.FormGroup(
    [
        html.P('Επιλογή Χώρας', style={
            'textAlign': 'center'
        }),
        dcc.Dropdown(
            id='dropdown',
            options=[{'label': i, 'value': i} for i in countriesUnique],
            value='Όλες',
            multi=False,
            style={'backgroundColor': '#1e243a'}
        ),
        html.Br(),
        html.P('Επιλογή Πηγής', style={
            'textAlign': 'center'
        }),
        dbc.Card([dbc.RadioItems(
            id='radio_items',
            options=[{
                'label': 'Όλες',
                'value': 'value1'
            },
                {
                'label': 'News247',
                'value': 'value2'
            },
                {
                    'label': 'Capital',
                    'value': 'value3'
                },
                {
                    'label': 'iefimerida',
                    'value': 'value4'
                }
            ],
            value='value1',
            style={
                'margin': 'auto'
            }
        )]),
    ]
)

sidebar = html.Div(
    [
        html.H2('Parameters', style={'textAlign': 'center','color': '#ffffff'}),
        html.Hr(),
        controls
    ],
    style=SIDEBAR_STYLE,
)

content_first_row = dbc.Row(
    [

        dbc.Col(html.Div([
                html.Section(id="slideshow", children=[
                    html.Div(id="slideshow-container", children=[
                        html.Div(id="image"),
                        dcc.Interval(id='interval', interval=3000)
                    ])
                ])        ], style={'background-color': '#2e3859','padding': '2%','min-height':'300px'}), md=4),
        dbc.Col(
            dcc.Graph(id='graph2', figure=fig2), md=4
        ),
        dbc.Col(
            dcc.Graph(id='graph3',figure=fig), md=4
        )
    ]
)

content_second_row = dbc.Row(
    [
        dbc.Col(
            html.Div(children=[
            dt.DataTable(id='my-final-result', 
            columns=[{"name": 'Τίτλος Άρθρου', "id": 'title'},
                    {"name": 'Σύντομη Περιγραφή', "id": 'text'},
                    {"name": 'Ημερομηνία Καταχώρησης', "id": 'time'},
                    {"name": 'Χώρα Αναφοράς', "id": 'country'}],
            style_header={'backgroundColor': '#2e3959','font-weight':'bold','text-align':'left','padding':'5px','font-size':'16px'},
            style_cell={'backgroundColor': '#2e3959','color': 'white','border': '0px'},
            style_data={'whiteSpace': 'normal','minWidth': '50px', 'width': 'auto', 'maxWidth': '280px','height': 'auto','text-align':'left','padding':'5px'},
            style_data_conditional=[{'if': {'column_id': 'country',},'text-transform': 'capitalize'}],
            page_size= 10,
            ),dcc.Interval(id='crawl-interval',interval=60000) ],style={'margin-left': '15px','margin-right': '15px'}), md=12 )
    ], style={'margin-top': '2%'}
)

content = html.Div(
    [
        html.H2('News Analysis - Παπαδημητρίου Θεόδωρος', style={'textAlign': 'center','color': '#ffffff','padding-top':'20px'}),
        html.Hr(),
        content_first_row,
        content_second_row,
    ],
    style=CONTENT_STYLE
)

app.layout = html.Div([sidebar, content], style={
        'background-color': '#1e243a'
    })


@app.callback(Output('my-final-result', 'data'), Input('crawl-interval', 'n_intervals'), Input('radio_items', 'value'))
def crawlTest(n, value):
    if value=='value1':
        df247 = crawl247()
        capital = crawlcapital()
        iefimerida = crawliefimerida()
        temp = vectorization(df247, capital, iefimerida)
    if value=='value2':
        temp=crawl247()
    if value=='value3':
        temp=crawlcapital()
    if value=='value4':
        temp=crawliefimerida()

    return temp.to_dict('records_final')

@app.callback(Output('image', 'children'),
              [Input('interval', 'n_intervals')])

def display_image(n):    
    imagesurl = frontDf1['image']
    titleurl = frontDf1['title']
    return html.Img(src=imagesurl[n % imagesurl.size], style={'width':'100%','margin-bottom':'2%'}), html.H4(titleurl[n % titleurl.size], style={'font-size':'16px'})

if __name__ == '__main__':
    app.run_server(debug=True)
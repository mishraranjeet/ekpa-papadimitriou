import base64
import os.path
import re
from datetime import date, datetime
from io import BytesIO

import dash
import dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash_html_components as html
import dash_table as dt
import matplotlib.pyplot as plt
import nltk
import pandas as pd
import plotly
import plotly.express as px
import plotly.graph_objs as go
import requests
from bs4 import BeautifulSoup
from dash.dependencies import Input, Output

# nltk.download('stopwords')
from nltk.corpus import stopwords
from wordcloud import STOPWORDS, ImageColorGenerator, WordCloud

from crawldash import crawl247, crawlcapital, crawliefimerida, vectorization

greek_stopwords = stopwords.words("greek")
greek_stopwords.append("γιατί")

agent = {
    "User-Agent": "Mozilla/5.0 (Windows NT 6.3; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/59.0.3071.115 Safari/537.36"
}

df247 = crawl247()
capital = crawlcapital()
iefimerida = crawliefimerida()
frontDf1 = vectorization(df247, capital, iefimerida)

yValue = frontDf1["3let"].value_counts()
xValue = frontDf1["country"].value_counts()
countriesUnique = frontDf1["country"].unique()

fig2 = px.bar(x=xValue.index, y=xValue, template="plotly_dark")
fig2.update_traces(marker_color="#fc4363")
fig2.update_layout(
    yaxis_visible=False,
    margin=dict(l=0, r=0, b=0, t=0, pad=0),
    height=350,
    paper_bgcolor="#1a1332",
    plot_bgcolor="#1a1332",
)

colorscale = [
    "#f691b4",
    "#f692b4",
    "#f36597",
    "#ee407d",
    "#ed1966",
    "#db1562",
    "#c7125f",
    "#b40d5b",
]

data = dict(
    type="choropleth",
    locations=yValue.index,
    colorscale=colorscale,
    z=yValue,
    text=yValue.index,
)

layout = dict(
    geo=dict(
        showframe=False,
        countrycolor="#1d2339",
        showocean=True,
        oceancolor="#1a1332",
        coastlinecolor="#1a1332",
        landcolor="#7999fe",
        projection={"type": "mercator"},
    )
)

fig = go.Figure(data=[data], layout=layout)
fig.update_geos(fitbounds="locations")
fig.update_layout(
    template="plotly_dark",
    margin=dict(l=0, r=0, b=0, t=0, pad=0),
    height=350,
    coloraxis_showscale=False,
    paper_bgcolor="#1a1332",
    plot_bgcolor="#1a1332",
)

app = dash.Dash(
    __name__,
    external_stylesheets=[dbc.themes.DARKLY],
    meta_tags=[{"name": "viewport", "content": "width=device-width, initial-scale=1"}],
)

server = app.server

controls = dbc.FormGroup(
    [
        dcc.DatePickerSingle(
            id="date-picker-range",
            min_date_allowed=datetime(2020, 12, 5),
            max_date_allowed=datetime.now(),
        ),
        html.P("Επιλογή Χώρας"),
        dcc.Dropdown(
            id="dropdown",
            options=[{"label": i, "value": i} for i in countriesUnique],
            value="Όλες",
            multi=False,
        ),
        html.Br(),
        html.P("Επιλογή Πηγής"),
        dbc.Card(
            [
                dbc.RadioItems(
                    id="radio_items",
                    options=[
                        {"label": "Όλες", "value": "value1"},
                        {"label": "News247", "value": "value2"},
                        {"label": "Capital", "value": "value3"},
                        {"label": "iefimerida", "value": "value4"},
                    ],
                    value="value1",
                    style={"margin": "auto"},
                )
            ]
        ),
    ]
)

sidebar = html.Div(
    id="sidebar",
    children=[html.H2("Parameters"), html.Hr(), controls],
)

content_first_row = dbc.Row(
    [
        dbc.Col(
            html.Div(
                id="firstrow",
                children=[
                    html.Section(
                        id="slideshow",
                        children=[
                            html.Div(
                                id="slideshow-container",
                                children=[
                                    html.Div(id="image"),
                                    dcc.Interval(id="interval", interval=3000),
                                ],
                            )
                        ],
                    )
                ],
            ),
            width=4,
            xs=12,
            md=4,
        ),
        dbc.Col(dcc.Graph(id="graph2", figure=fig2), width=4, xs=12, md=4),
        dbc.Col(dcc.Graph(id="graph3", figure=fig), width=4, xs=12, md=4),
    ]
)

content_second_row = dbc.Row(
    id="secondrow-main",
    children=[
        dbc.Col(
            html.Div(
                id="secondrow",
                children=[
                    dt.DataTable(
                        id="my-final-result",
                        columns=[
                            {"name": "Τίτλος", "id": "title"},
                            {"name": "Ημερομηνία", "id": "time"},
                            {"name": "Χώρα", "id": "country"},
                        ],
                        style_header={
                            "backgroundColor": "#1a1332",
                            "font-weight": "bold",
                            "text-align": "left",
                            "padding": "5px",
                            "font-size": "16px",
                        },
                        style_cell={
                            "backgroundColor": "#242438",
                            "color": "white",
                            "border": "0px",
                        },
                        style_data={
                            "whiteSpace": "normal",
                            "minWidth": "50px",
                            "width": "auto",
                            "maxWidth": "280px",
                            "height": "auto",
                            "text-align": "left",
                            "padding": "5px",
                        },
                        style_data_conditional=[
                            {
                                "if": {
                                    "column_id": "country",
                                },
                                "text-transform": "capitalize",
                            }
                        ],
                        page_size=5,
                    ),
                    dcc.Interval(id="crawl-interval", interval=60000),
                ],
            ),
            width=4,
            xs=12,
            md=4,
        ),
        dbc.Col(html.Img(id="image_wc"), width=4, xs=12, md=4),
        dbc.Col(
            id="countcards",
            children=[
                dbc.Card(
                    id="card247",
                    children=[html.H4("News247 Scraped"), html.H3(len(df247))],
                ),
                dbc.Card(
                    id="cardcapital",
                    children=[html.H4("Capital Scraped"), html.H3(len(capital))],
                ),
                dbc.Card(
                    id="cardiefimerida",
                    children=[html.H4("iefimerida Scraped"), html.H3(len(iefimerida))],
                ),
            ],
            width=4,
            xs=12,
            md=4,
        ),
    ],
)

content_third_row = dbc.Row(
    id="thirdrow-main",
    children=[
        dbc.Col(
            html.Div(
                id="thirdrow",
                children=[
                    dt.DataTable(
                        id="datetime_df",
                        columns=[
                            {"name": "Τίτλος", "id": "title"},
                            {"name": "Σύντομη Περιγραφή", "id": "text"},
                            {"name": "Ημερομηνία", "id": "time"},
                            {"name": "Χώρα", "id": "country"},
                        ],
                        style_header={
                            "backgroundColor": "#1a1332",
                            "font-weight": "bold",
                            "text-align": "left",
                            "padding": "5px",
                            "font-size": "16px",
                        },
                        style_cell={
                            "backgroundColor": "#242438",
                            "color": "white",
                            "border": "0px",
                        },
                        style_data={
                            "whiteSpace": "normal",
                            "minWidth": "50px",
                            "width": "auto",
                            "maxWidth": "100%",
                            "height": "auto",
                            "text-align": "left",
                            "padding": "5px",
                        },
                        style_data_conditional=[
                            {
                                "if": {
                                    "column_id": "country",
                                },
                                "text-transform": "capitalize",
                            }
                        ],
                        page_size=5,
                    ),
                ],
            ),
            width=12,
            xs=12,
            md=12,
        ),
    ],
)

content = html.Div(
    id="content",
    children=[
        content_first_row,
        content_second_row,
        content_third_row,
    ],
)

app.layout = html.Div(
    children=[
        html.H2("News Analysis - Παπαδημητρίου Θεόδωρος", style={"padding": "2%"}),
        html.Hr(style={"margin": "0"}),
        sidebar,
        content,
    ],
    style={"background-color": "#160d28"},
)


@app.callback(
    Output("my-final-result", "data"),
    Input("crawl-interval", "n_intervals"),
    Input("radio_items", "value"),
)
def crawlTest(n, value):
    if value == "value1":
        temp = vectorization(df247, capital, iefimerida)
    if value == "value2":
        temp = pd.read_csv("news247.csv")
    if value == "value3":
        temp = pd.read_csv("capital.csv")
    if value == "value4":
        temp = pd.read_csv("iefimerida.csv")

    return temp.to_dict("records")


@app.callback(
    Output("datetime_df", "data"),
    Input("date-picker-range", "date"),
)
def pickadate(date_value):
    if date_value is not None:
        date_object = date.fromisoformat(date_value)
        date_string = date_object.strftime("%Y-%m-%d")
        if os.path.isfile(date_string + ".csv"):
            print("Το αρχείο δεν υπάρχει")
            temp = pd.read_csv(date_string + ".csv")
        else:
            print("Το αρχείο δεν υπάρχει")
            temp = pd.DataFrame()
    return temp.to_dict("records")


@app.callback(Output("image", "children"), [Input("interval", "n_intervals")])
def display_image(n):
    imagesurl = frontDf1["image"]
    titleurl = frontDf1["title"]
    return html.Img(src=imagesurl[n % imagesurl.size]), html.H4(
        titleurl[n % titleurl.size]
    )


@app.callback(Output("image_wc", "src"), [Input("image_wc", "id")])
def make_image(b):
    d = " ".join(lyr for lyr in frontDf1.title)
    d = re.sub(r"[^\w]", " ", d)
    shortword = re.compile(r"\W*\b\w{1,5}\b")
    d = shortword.sub("", d)
    d = d.lower()
    wc = WordCloud(
        stopwords=greek_stopwords, background_color="#160d28", height=350, max_words=50
    ).generate(d)
    img = BytesIO()
    plt.figure()
    plt.imshow(wc, interpolation="bilinear")
    plt.axis("off")
    plt.savefig(
        img, format="png", dpi=600, bbox_inches="tight", pad_inches=0
    )  # save to the above file object
    data = base64.b64encode(img.getbuffer()).decode("utf8")  # encode to html elements
    plt.close()

    return ["data:image/png;base64,{}".format(data)]


if __name__ == "__main__":
    app.run_server(debug=True)

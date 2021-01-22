import re
from datetime import date, datetime
from urllib.request import Request, urlopen

import matplotlib.pyplot as plt
import nltk
import numpy as np
import pandas as pd
import requests
from bs4 import BeautifulSoup
from lxml.html import fromstring, html5parser
from nltk.corpus import stopwords
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

greek_stopwords = stopwords.words("greek")

countries = pd.read_csv("countries.csv")


agent = {
    "User-Agent": "Mozilla/5.0 (Windows NT 6.3; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/59.0.3071.115 Safari/537.36"
}

pages247 = ("politiki/", "koinonia/", "oikonomia/", "kosmos/")
pagescap = ("politiki", "eidiseis", "oikonomia", "diethni")
pagesiefim = ("politiki", "ellada", "oikonomia", "kosmos")
pagesbeast = ("politiki", "greece", "financial", "world")


def crawl247(pages=pages247, agent=agent):
    df247 = pd.DataFrame()
    print("crawling news247...")
    for page in pages247:
        URL = "https://www.news247.gr/" + str(page)

        r1 = requests.get(URL)
        coverpage = r1.content
        soup1 = BeautifulSoup(coverpage, "html5lib")
        coverpage_news = soup1.find_all("h3", class_="article__title bold")
        coverpage_news_text = soup1.find_all("p", class_="article__leadtext")
        coverpage_news_time = soup1.find_all("time")
        coverpage_news_image = soup1.find_all("img", {"src": re.compile(".jpg")})

        coverpage_news = [i.text for i in coverpage_news]

        column_names = ["title", "text", "time", "image"]

        S = pd.DataFrame(
            list(
                zip(
                    coverpage_news,
                    coverpage_news_text,
                    coverpage_news_time,
                    coverpage_news_image,
                )
            ),
            columns=column_names,
        ).astype(str)

        df247 = df247.append(S)

    df247 = df247.replace(r"\n", " ", regex=True)
    df247 = df247.replace(r"\s+", " ", regex=True)
    df247 = df247.replace(r"^\['|'\]$", "", regex=True)
    df247["time"] = df247["time"].str.extract(r"(\d{4}-\d{2}-\d{2} \d{2}:\d{2})")

    df247["title"] = df247["title"].astype(str)
    df247["text"] = df247["text"].astype(str)
    df247["time"] = df247["time"].astype(str)

    df247["text"] = df247["text"].replace(
        '<p class="article__leadtext">', "", regex=True
    )
    df247["text"] = df247["text"].replace("</p>", "", regex=True)

    df247["time"] = pd.to_datetime(df247["time"])
    df247 = df247.reset_index(drop=True)

    df247["image"] = df247["image"].str.extract(
        r"(http[s]?:\/\/(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+)"
    )

    countries["name"] = countries["name"].str.lower()
    df247["country"] = df247["title"].str.lower()
    df247["country"] = df247["country"].str.replace(r"[^\w\s]*", "").str.strip()
    countries["name"] = countries["name"].str.replace(r"[^\w\s]*", "").str.strip()
    df247["country"] = (
        df247["country"].astype(str).str.extract(f"({'|'.join(countries['name'])})")
    )
    df247["country"] = df247["country"].replace(np.nan, "ελλάδα", regex=True)
    df247["countrycode"] = df247["country"]
    df247["countrycode"] = df247["countrycode"].map(
        countries.set_index("name")["country"]
    )
    df247["countrycode"] = df247["countrycode"].replace(np.nan, "GR", regex=True)

    return df247


def crawlcapital(pages=pagescap, agent=agent):
    print("crawling capital...")
    capital = pd.DataFrame()
    for page in pagescap:
        URL = "https://www.capital.gr/" + str(page)

        r1 = requests.get(URL)
        coverpage = r1.content
        soup1 = BeautifulSoup(coverpage, "html5lib")
        coverpage_news = soup1.find_all("h2", class_="bold")
        coverpage_news_text = soup1.find_all("div", class_="item__description")
        untime = soup1.find_all("span", class_="time")
        date = soup1.find_all("span", class_="date")

        coverpage_news_image = soup1.find_all("div", class_="image__wrapper")

        coverpage_news = [i.text for i in coverpage_news]

        column_names = ["title", "text", "ttime", "date", "image"]

        S = pd.DataFrame(
            list(
                zip(
                    coverpage_news,
                    coverpage_news_text,
                    untime,
                    date,
                    coverpage_news_image,
                )
            ),
            columns=column_names,
        ).astype(str)

        capital = capital.append(S)

    capital = capital.replace(r"\n", " ", regex=True)
    capital = capital.replace(r"\s+", " ", regex=True)
    capital = capital.replace(r"^\['|'\]$", "", regex=True)
    capital["ttime"] = capital["ttime"].str.extract(r"(\d{2}:\d{2})")
    capital["date"] = capital["date"].str.extract(r"(\d{2}/\d{2})")

    capital["title"] = capital["title"].astype(str)
    capital["text"] = capital["text"].astype(str)
    capital["ttime"] = capital["ttime"].astype(str)
    capital["date"] = capital["date"].astype(str) + "/2020"

    capital["text"] = capital["text"].replace(
        '<p class="feed-article-excerpt hidden-xs">', "", regex=True
    )
    capital["text"] = capital["text"].str.replace(r"[\<\[].*?[\>\]]", "", regex=True)

    capital["text"] = capital["text"].replace("</p>", "", regex=True)

    capital["ttime"] = capital["ttime"].dropna()
    capital["date"] = capital["date"].dropna()

    capital["time"] = capital[["date", "ttime"]].agg(" - ".join, axis=1)

    capital["time"] = pd.to_datetime(capital["time"])

    capital = capital.drop(["ttime", "date"], axis=1)
    capital = capital.reset_index(drop=True)

    capital["image"] = capital["image"].str.extract(
        r"(http[s]?:\/\/([/|.|\w|\s])*\.(?:jpg|gif|png|PNG|JPG))"
    )

    capital = capital[["title", "text", "time", "image"]]

    countries["name"] = countries["name"].str.lower()
    capital["country"] = capital["title"].str.lower()
    capital["country"] = capital["country"].str.replace(r"[^\w\s]*", "").str.strip()
    countries["name"] = countries["name"].str.replace(r"[^\w\s]*", "").str.strip()
    capital["country"] = (
        capital["country"].astype(str).str.extract(f"({'|'.join(countries['name'])})")
    )
    capital["country"] = capital["country"].replace(np.nan, "ελλάδα", regex=True)
    capital["countrycode"] = capital["country"]
    capital["countrycode"] = capital["countrycode"].map(
        countries.set_index("name")["country"]
    )
    capital["countrycode"] = capital["countrycode"].replace(np.nan, "GR", regex=True)

    return capital


def crawliefimerida(pages=pagesiefim):
    print("crawling iefimerida...")
    iefimerida = pd.DataFrame()
    for page in pagesiefim:
        URL = "https://www.iefimerida.gr/" + str(page)

        req = Request(URL, headers={"User-Agent": "Mozilla/5.0"})

        webpage = urlopen(req).read()
        page_soup = BeautifulSoup(webpage, "html5lib")

        coverpage_news = page_soup.find_all("h3")
        coverpage_news_text = page_soup.find_all("div", class_="field-summary")
        time = page_soup.find_all("span", class_="created")

        coverpage_news_image = page_soup.find_all("div", class_="image-wrapper")

        coverpage_news = [i.text for i in coverpage_news]

        column_names = ["title", "text", "time", "image"]

        S = pd.DataFrame(
            list(zip(coverpage_news, coverpage_news_text, time, coverpage_news_image)),
            columns=column_names,
        ).astype(str)

        iefimerida = iefimerida.append(S)

    iefimerida = iefimerida.replace(r"\n", " ", regex=True)
    iefimerida = iefimerida.replace(r"\s+", " ", regex=True)
    iefimerida = iefimerida.replace(r"^\['|'\]$", "", regex=True)
    iefimerida["time"] = iefimerida["time"].str.extract(
        r"(\d{2}\|\d{2}\|\d{4} \| \d{2}\:\d{2})"
    )
    iefimerida["time"] = iefimerida["time"].str.replace("|", "/", regex=True)

    iefimerida["title"] = iefimerida["title"].astype(str)
    iefimerida["text"] = iefimerida["text"].astype(str)
    iefimerida["time"] = iefimerida["time"].astype(str)

    iefimerida["text"] = iefimerida["text"].replace(
        '<p class="feed-article-excerpt hidden-xs">', "", regex=True
    )
    iefimerida["text"] = iefimerida["text"].str.replace(
        r"[\<\[].*?[\>\]]", "", regex=True
    )
    iefimerida["text"] = iefimerida["text"].replace("</p>", "", regex=True)

    iefimerida = iefimerida[~iefimerida.time.str.contains("nan")]

    iefimerida["time"] = pd.to_datetime(iefimerida["time"])

    iefimerida = iefimerida.drop([iefimerida.index[0]])
    iefimerida = iefimerida.reset_index(drop=True)

    iefimerida["image"] = iefimerida["image"].str.extract(r"src=([^>]+)\"")
    iefimerida["image"] = iefimerida["image"].str.replace('"', "")
    iefimerida["image"] = iefimerida["image"].str.replace(r"\?.*", "", regex=True)
    iefimerida["image"] = "https://www.iefimerida.gr" + iefimerida["image"].astype(str)

    iefimerida = iefimerida[["title", "text", "time", "image"]]

    countries["name"] = countries["name"].str.lower()
    iefimerida["country"] = iefimerida["title"].str.lower()
    iefimerida["country"] = (
        iefimerida["country"].str.replace(r"[^\w\s]*", "").str.strip()
    )
    countries["name"] = countries["name"].str.replace(r"[^\w\s]*", "").str.strip()
    iefimerida["country"] = (
        iefimerida["country"]
        .astype(str)
        .str.extract(f"({'|'.join(countries['name'])})")
    )
    iefimerida["country"] = iefimerida["country"].replace(np.nan, "ελλάδα", regex=True)
    iefimerida["countrycode"] = iefimerida["country"]
    iefimerida["countrycode"] = iefimerida["countrycode"].map(
        countries.set_index("name")["country"]
    )
    iefimerida["countrycode"] = iefimerida["countrycode"].replace(
        np.nan, "GR", regex=True
    )

    return iefimerida


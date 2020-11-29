from urllib.request import Request, urlopen
import requests
from bs4 import BeautifulSoup
import pandas as pd
import re
from datetime import datetime

pages247 = ('politiki/','koinonia/','oikonomia/','kosmos/')
pagescap = ('politiki','eidiseis','oikonomia','diethni')
pagesiefim = ('politiki','ellada','oikonomia','kosmos')
pagesbeast = ('politiki','greece','financial','world')

df247 = pd.DataFrame()
capital = pd.DataFrame()
iefimerida = pd.DataFrame()
newsbeast = pd.DataFrame()

for page in pages247:
  URL="https://www.news247.gr/" + str(page)

  r1 = requests.get(URL)
  coverpage = r1.content
  soup1 = BeautifulSoup(coverpage, 'html.parser')
  results1 = soup1.find("div", {"class": "teaser__content"})
  results = soup1.findAll("article", {"class": "teaser__article"})
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

for page in pagescap:
  URL="https://www.capital.gr/" + str(page)
  soup = BeautifulSoup(URL)

  results1 = soup.find("div", {"class": "articles__list"})
  results = soup.findAll("div", {"class": "article"})
  r1 = requests.get(URL)
  coverpage = r1.content
  soup1 = BeautifulSoup(coverpage, 'html.parser')
  coverpage_news = soup1.find_all('h2', class_='bold')
  coverpage_news_text = soup1.find_all('div', class_='item__description')
  untime = soup1.find_all('span', class_='time')
  date = soup1.find_all('span', class_='date') 

  coverpage_news_image = soup1.find_all('img', {'src':re.compile('.jpg')})

  coverpage_news = [i.text for i in coverpage_news]

  column_names = ["title", "text", "ttime", "date", "image"]

  S = pd.DataFrame(list(zip(coverpage_news, coverpage_news_text, untime, date, coverpage_news_image)), columns =column_names).astype(str)
  capital = capital.append(S)

capital = capital.replace(r'\n',' ', regex=True) 
capital = capital.replace(r'\s+', ' ', regex=True)
capital = capital.replace(r"^\['|'\]$","", regex=True)
capital['ttime']=capital['ttime'].str.extract(r'(\d{2}:\d{2})')
capital['date']=capital['date'].str.extract(r'(\d{2}/\d{2})')

capital['title'] = capital['title'].astype(str)
capital['text'] = capital['text'].astype(str)
capital['ttime'] = capital['ttime'].astype(str)
capital['date'] = capital['date'].astype(str) +'/2020'

capital['text'] = capital['text'].replace('<p class="feed-article-excerpt hidden-xs">', '', regex=True)
capital['text'] = capital['text'].str.replace(r"[\<\[].*?[\>\]]", "", regex=True)


capital['text'] = capital['text'].replace('</p>', '', regex=True)

capital['ttime'] = capital['ttime'].dropna()
capital['date'] = capital['date'].dropna()

capital['time'] = capital[['date', 'ttime']].agg(' - '.join, axis=1)

capital['time']= pd.to_datetime(capital['time'])

capital = capital.drop(['ttime', 'date'], axis=1)
capital = capital.reset_index(drop=True)

for page in pagesiefim:
  URL="https://www.iefimerida.gr/" + str(page)
  
  req = Request(URL , headers={'User-Agent': 'Mozilla/5.0'})

  webpage = urlopen(req).read()
  page_soup = BeautifulSoup(webpage, "html.parser")

  coverpage_news = page_soup.find_all('h3')
  coverpage_news_text = page_soup.find_all('div', class_='field-summary')
  time = page_soup.find_all('span', class_='created')

  coverpage_news_image = page_soup.find_all('picture', class_='lazy horizontal_rectangle')

  coverpage_news = [i.text for i in coverpage_news]

  column_names = ["title", "text", "time", "image"]

  S = pd.DataFrame(list(zip(coverpage_news, coverpage_news_text, time, coverpage_news_image)), columns =column_names).astype(str)
  iefimerida = iefimerida.append(S)

iefimerida = iefimerida.replace(r'\n',' ', regex=True) 
iefimerida = iefimerida.replace(r'\s+', ' ', regex=True)
iefimerida = iefimerida.replace(r"^\['|'\]$","", regex=True)
iefimerida['time']=iefimerida['time'].str.extract(r'(\d{2}\|\d{2}\|\d{4} \| \d{2}\:\d{2})')
iefimerida['time']=iefimerida['time'].str.replace("|", "/", regex=True)


iefimerida['title'] = iefimerida['title'].astype(str)
iefimerida['text'] = iefimerida['text'].astype(str)
iefimerida['time'] = iefimerida['time'].astype(str)

iefimerida['text'] = iefimerida['text'].replace('<p class="feed-article-excerpt hidden-xs">', '', regex=True)
iefimerida['text'] = iefimerida['text'].str.replace(r"[\<\[].*?[\>\]]", "", regex=True)


iefimerida['text'] = iefimerida['text'].replace('</p>', '', regex=True)

iefimerida = iefimerida[~iefimerida.time.str.contains("nan")]

iefimerida['time']= pd.to_datetime(iefimerida['time'])


iefimerida = iefimerida.drop([iefimerida.index[0]])
iefimerida = iefimerida.reset_index(drop=True)

for page in pagesbeast:
  URL="https://www.newsbeast.gr/" + str(page)
  soup = BeautifulSoup(URL)

  results1 = soup.find("div", {"class": "feed category-feed"})
  results = soup.findAll("article", {"class": "feed-article"})
  r1 = requests.get(URL)
  coverpage = r1.content
  soup1 = BeautifulSoup(coverpage, 'html.parser')
  coverpage_news = soup1.find_all('h2', class_='hidden-xs')
  coverpage_news_text = soup1.find_all('p', class_='feed-article-excerpt')
  ttime = soup1.find_all('div', class_='article-top-meta-time')
  date = soup1.find_all('div', class_='article-top-meta-date') 

  coverpage_news_image = soup1.find_all('img', {'src':re.compile('.jpg')})

  coverpage_news = [i.text for i in coverpage_news]

  column_names = ["title", "text", "ttime", "date", "image"]

  S = pd.DataFrame(list(zip(coverpage_news, coverpage_news_text, ttime, date, coverpage_news_image)), columns =column_names).astype(str)
  newsbeast = newsbeast.append(S)

newsbeast = newsbeast.replace(r'\n',' ', regex=True) 
newsbeast = newsbeast.replace(r'\s+', ' ', regex=True)
newsbeast = newsbeast.replace(r"^\['|'\]$","", regex=True)
newsbeast['ttime']=newsbeast['ttime'].str.extract(r'(\d{2}:\d{2})')
newsbeast['date']=newsbeast['date'].str.extract(r'(r\d{2}/\d{2}/\d{4})')

newsbeast['title'] = newsbeast['title'].astype(str)
newsbeast['text'] = newsbeast['text'].astype(str)
newsbeast['ttime'] = newsbeast['ttime'].astype(str)
newsbeast['date'] = newsbeast['date'].astype(str)

newsbeast['text'] = newsbeast['text'].replace('<p class="feed-article-excerpt hidden-xs">', '', regex=True)
newsbeast['text'] = newsbeast['text'].str.replace(r"[\<\[].*?[\>\]]", "", regex=True)
newsbeast['text'] = newsbeast['text'].replace('</p>', '', regex=True)

newsbeast = newsbeast[~newsbeast.ttime.str.contains("nan")]
newsbeast = newsbeast[~newsbeast.date.str.contains("nan")]

newsbeast['time'] = newsbeast[['date', 'ttime']].agg(' - '.join, axis=1)

newsbeast = newsbeast.drop(['ttime', 'date'], axis=1)
newsbeast = newsbeast.reset_index(drop=True)

newsbeast['time']= pd.to_datetime(newsbeast['time'])
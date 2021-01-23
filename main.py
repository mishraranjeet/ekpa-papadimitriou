from flask import Flask
from flask import request, jsonify, render_template, redirect
from crawl_scrapper import crawl247,crawlcapital,crawliefimerida
from model.models import insert_to_db,connect_to_db
import datetime
from datetime import timedelta
import pandas as pd

flask_app = Flask(__name__)


@flask_app.route('/')
def home():
    return jsonify('Hello World!!!')



@flask_app.route('/scrapper',methods=['GET', 'POST'])
def run_scrapper():
  try:
    df247 = crawl247().to_dict(orient='records')
    capital = crawlcapital().to_dict(orient='records')
    iefimerida = crawliefimerida().to_dict(orient='records')
    insert_to_db('news247',df247)
    insert_to_db('capital',capital)
    insert_to_db('iefimerida',iefimerida)
    return jsonify({'success':True,'data_saved_time':datetime.datetime.strftime(datetime.datetime.now(),'%Y-%m-%d %H:%M:%S')})
  except Exception as e:
    print("error on saving data: ",e)
    return jsonify({'success':False})

@flask_app.route('/data/<daterange>',methods=['GET', 'POST'])
def show_data(daterange):
  conn,db=connect_to_db()
  # daterange format must be in days for example 2
  news_date_range=datetime.datetime.now()-timedelta(days=int(daterange))
  news_date_from=datetime.datetime.strftime(news_date_range,'%Y-%m-%d %H:%M:%S')
  news_date_to=datetime.datetime.strftime(datetime.datetime.now(),'%Y-%m-%d %H:%M:%S')
  query=""" select * from newscrawler where newstime between '{lower}' and '{upper}'
          ;""".format(lower=news_date_from,upper=news_date_to)
  print("query:",query)
  df = pd.read_sql_query(query, conn)

  return jsonify(df.to_dict(orient='records'))



if __name__ == '__main__':
  print("ia ma hebkjaebnvibav")
  flask_app.run(debug=True)



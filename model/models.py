import psycopg2
import pandas as pd 


def connect_to_db():
  db_connection = psycopg2.connect(
    host="18.220.76.242",
    database="newscrawl",
    user="postgres",
    password="helloworld1!")
  db_connection.set_session(autocommit=True)
  cursor = db_connection.cursor()
  cursor.execute('SELECT version()')
  db_version = cursor.fetchone()
  print(db_version)
  return db_connection,cursor


conn,db=connect_to_db()
def create_table():
  try:
    table_creation=["""
                    CREATE TABLE newscrawler (
                    id serial PRIMARY KEY,
                    title VARCHAR ( 500 ) ,
                    newstext VARCHAR ( 2000 ) ,
                    newstime VARCHAR ( 500 ) ,
                    newsource VARCHAR ( 500 ) ,
                    imagelink VARCHAR ( 500 ) ,
                    country VARCHAR ( 500 ) ,
                    countrycode VARCHAR ( 500 ) ,
                    newslet VARCHAR ( 500 ) ,
                    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
                    updated_at TIMESTAMP NOT NULL DEFAULT NOW()
                  );
                ""","""
                    CREATE TABLE  capitalcrawler (
                    id serial PRIMARY KEY,
                    title VARCHAR ( 500 ) ,
                    newstext VARCHAR ( 2000 ) ,
                    newstime VARCHAR ( 500 ) ,
                    newsource VARCHAR ( 500 ) ,
                    imagelink VARCHAR ( 500 ) ,
                    country VARCHAR ( 500 ) ,
                    countrycode VARCHAR ( 500 ) ,
                    newslet VARCHAR ( 500 ) ,
                    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
                    updated_at TIMESTAMP NOT NULL DEFAULT NOW()
                  );
                """,
                """
                  CREATE TABLE  iefimeridacrawler (
                    id serial PRIMARY KEY,
                    title VARCHAR ( 500 ) ,
                    newstext VARCHAR ( 2000 ) ,
                    newstime VARCHAR ( 500 ) ,
                    newsource VARCHAR ( 500 ) ,
                    imagelink VARCHAR ( 500 ) ,
                    country VARCHAR ( 500 ) ,
                    countrycode VARCHAR ( 500 ) ,
                    newslet VARCHAR ( 500 ) ,
                    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
                    updated_at TIMESTAMP NOT NULL DEFAULT NOW()
                  );
                """]

    for table in table_creation:
      db.execute(table)
    db.close()
    return True   
  except Exception as e :
    print("error:",e)
    return False
  
def insert_to_db(table,new_source,data=None):
  if data is None:
    data=[]
  try:
    record_to_insert=[]
    if len(data)>0:
      for d in data:
        checkrecord=record_exists(table,d['title'])
        print("checkrecord:",checkrecord)
        if not checkrecord:
          title=str(d['title']).replace("'","''") if 'title' in d else None
          newstext=d['text'] if 'text' in d else None
          newstime=d['time'] if 'time' in d else None
          newsource=new_source
          imagelink=d['image'] if 'image' in d else None
          country=d['country'] if 'country' in d else None
          countrycode=d['countrycode'] if 'countrycode' in d else None
          newslet=d['3let'] if '3let' in d else None
          db_data=(title,newstext,newstime,newsource,imagelink,country,countrycode,newslet)
          record_to_insert.append(db_data)

    db_insert_query = """ INSERT INTO {tablename} (title, newstext, newstime,newsource,imagelink,country,countrycode,newslet) VALUES (%s,%s,%s,%s,%s,%s,%s,%s)""".format(tablename=table)
    for record in record_to_insert :
      db.execute(db_insert_query, record)
      conn.commit()
    db.close()
    return True
  except Exception as e :
    print("error:",e)
    return False


def record_exists(table,title):
  title=str(title).replace("'","''")
  query="""SELECT id FROM {table} WHERE title = '{title}'""".format(table=table,title=title)
  db.execute(query)
  return db.fetchone() is not None



if __name__ == '__main__':
  # print(create_table())
  df = pd.read_csv("news.csv") 
  data=df.to_dict(orient='records')
  print(insert_to_db('newscrawler','news247',data))

FROM python:3.8

RUN mkdir /ekpa-papadimitriou
WORKDIR /ekpa-papadimitriou

COPY requirements.txt /
RUN pip3 install -r /requirements.txt
RUN python -m nltk.downloader stopwords

COPY . ./
EXPOSE 8050

CMD [ "gunicorn", "--workers=5", "--threads=1", "-b 0.0.0.0:8000", "app:server"]
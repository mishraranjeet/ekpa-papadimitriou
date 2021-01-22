FROM python:3.8

RUN mkdir /ekpa-papadimitriou
WORKDIR /ekpa-papadimitriou
ADD . /ekpa-papadimitriou

COPY requirements.txt /
RUN pip3 install -r requirements.txt
RUN python -m nltk.downloader stopwords
RUN chmod 777 ./run.sh

EXPOSE 8000
CMD ["./run.sh"]

# CMD [ "gunicorn", "--workers=5", "--threads=1", "-b 0.0.0.0:8000", "app:server"]
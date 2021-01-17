 
FROM python:3.8.6

LABEL MAINTAINER="dkeysil dkeysil@protonmail.com"

WORKDIR /contribbot
ADD ./requirements.txt /contribbot/requirements.txt
RUN pip install -r requirements.txt
ADD . /contribbot

CMD python -u __main__.py

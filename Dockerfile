FROM python:3

RUN apt-get update && apt-get install -y gettext && apt-get install -y cron 

ADD requirements.txt .

RUN pip install -r requirements.txt

WORKDIR /usr/src/app

ADD . /usr/src/app

# Cron service

RUN echo "00 3 * * 1 root cd /usr/src/app && /usr/local/bin/python capture_data.py" >> /etc/crontab

RUN env >> /etc/environment

CMD sh cron.sh





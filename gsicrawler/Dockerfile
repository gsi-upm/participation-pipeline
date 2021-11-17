FROM python:3.6

RUN groupadd -g 999 crawler && \
    useradd -r -u 999 -g crawler crawler

RUN apt-get update && apt-get install -y \
    supervisor \
    && rm -rf /var/lib/apt/lists/*

ADD supervisor /etc/supervisor/supervisor.d
ADD supervisor/common.conf /etc/supervisord.conf

RUN mkdir -p /usr/src/app

ADD requirements.txt /usr/src/app/
RUN pip install -r /usr/src/app/requirements.txt
# RUN pip install --upgrade git+https://github.com/twintproject/twint.git@origin/master#egg=twint
ADD /twint /twint
RUN pip install -e /twint/src/twint

ADD . /usr/src/app

ENV LC_ALL C

# Web
EXPOSE 5000

# Celery Flower
EXPOSE 5555

ENV GSICRAWLER_BROKER=redis://redis:6379/
ENV GSICRAWLER_RESULT_BACKEND=redis://redis:6379/

USER crawler

WORKDIR /usr/src/app

ENTRYPOINT ["/usr/src/app/init.sh"]

CMD ["all"]

FROM python:3.10.5 AS python
WORKDIR /app

RUN apt-get update \
    && apt-get install -y \
        curl \
        libxrender1 \
        libjpeg62-turbo \
        fontconfig \
        libxtst6 \
        xfonts-75dpi \
        xfonts-base \
        xz-utils \
        chromium
RUN curl "https://github.com/wkhtmltopdf/packaging/releases/download/0.12.6-1/wkhtmltox_0.12.6-1.buster_amd64.deb" -L -o "wkhtmltopdf.deb"
RUN dpkg -i wkhtmltopdf.deb

COPY ./requirements.txt /requirements.txt
RUN pip install --upgrade pip
RUN pip install --no-cache-dir --upgrade -r /requirements.txt
COPY ./app/ /app/

RUN chmod +x ./entrypoint.sh
CMD ["./entrypoint.sh"]


FROM python:3.10.5 AS migration
COPY ./yoyo_migration/ /yoyo_migration/
COPY ./entrypoint_migrate.sh /entrypoint_migrate.sh
RUN pip install --upgrade pip
RUN pip install --no-cache-dir --upgrade yoyo-migrations==7.3.2
RUN pip install --no-cache-dir --upgrade psycopg2==2.9.3
RUN chmod +x /entrypoint_migrate.sh
ENTRYPOINT ./entrypoint_migrate.sh


FROM python:3.10.5 AS scheduler
WORKDIR /app
COPY ./requirements.txt /requirements.txt
RUN pip install --upgrade pip
RUN pip install --no-cache-dir --upgrade -r /requirements.txt
COPY ./app/ /app/
RUN chmod +x ./entrypoint_scheduler.sh
ENTRYPOINT ./entrypoint_scheduler.sh

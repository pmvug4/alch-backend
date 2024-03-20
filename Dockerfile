FROM python:3.10.5 AS python
WORKDIR /app

COPY ./requirements.txt /requirements.txt
RUN pip install --upgrade pip
RUN pip install --no-cache-dir --upgrade -r /requirements.txt
COPY ./app/ /app/

RUN chmod +x ./entrypoint.sh
CMD ["./entrypoint.sh"]


FROM python:3.10.5 AS migration

RUN pip install --upgrade pip
RUN pip install --no-cache-dir --upgrade yoyo-migrations==7.3.2
RUN pip install --no-cache-dir --upgrade psycopg2==2.9.3

COPY ./yoyo_migration/ /yoyo_migration/
COPY ./entrypoint_migrate.sh /entrypoint_migrate.sh

RUN chmod +x /entrypoint_migrate.sh
ENTRYPOINT ./entrypoint_migrate.sh

FROM python:3.11-slim-bookworm as base

LABEL version="1.0"
LABEL description="Reunite web image"

ARG DEBIAN_FRONTEND=noninteractive

RUN set -ex; \
    apt-get update && \
    apt-get install -qq --no-install-recommends wget curl locales libjemalloc2 ca-certificates tzdata libopenblas0 \
            build-essential cmake python3-dev libffi-dev unzip libaio1 python3-typing-extensions && \
    rm -rf /var/lib/apt/lists/*

# Oracle instant client
#RUN wget https://download.oracle.com/otn_software/linux/instantclient/1919000/instantclient-basic-linux.arm64-19.19.0.0.0dbru.zip && \
#    unzip instantclient-basic-linux.arm64-19.19.0.0.0dbru.zip && \
#    rm -fr instantclient-basic-linux.arm64-19.19.0.0.0dbru.zip && \
#    mkdir -p /opt/oracle && \
#    mv instantclient_19_19 /opt/oracle/ && \
#    (cd /opt/oracle && ln -s instantclient_19_19 instantclient)
#
#ENV PATH="$PATH:/opt/oracle/instantclient"
#RUN echo "/opt/oracle/instantclient" > /etc/ld.so.conf.d/oracle-instantclient.conf
#RUN ldconfig


RUN echo "deb http://apt.postgresql.org/pub/repos/apt $(lsb_release -cs)-pgdg main" > /etc/apt/sources.list.d/pgdg.list \
    && wget -qO- https://www.postgresql.org/media/keys/ACCC4CF8.asc | tee /etc/apt/trusted.gpg.d/pgdg.asc &>/dev/null
RUN set -ex; \
    apt-get update && \
    apt-get install -qq --no-install-recommends postgresql-client postgresql-common  && \
    rm -rf /var/lib/apt/lists/*


# locales to UTF-8
RUN locale-gen C.UTF-8 && /usr/sbin/update-locale LANG=C.UTF-8
ENV LC_ALL C.UTF-8

# better memory allocation
ENV LD_PRELOAD=/usr/lib/aarch64-linux-gnu/libjemalloc.so.2

# basic python settings for container
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# app environment
ENV PYTHONIOENCODING UTF-8
ENV PYTHONPATH /app/

# app dependencies
RUN pip install --no-cache-dir --upgrade pip wheel setuptools
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

WORKDIR /app/

ARG PORT=8000
ARG HOST=0.0.0.0
ENV HOST=${HOST}
ENV PORT=${PORT}

STOPSIGNAL SIGTERM
EXPOSE ${PORT}

ENTRYPOINT /usr/local/bin/gunicorn --access-logfile - \
            --workers 4 --keep-alive 5 \
            --max-requests 500 --max-requests-jitter 20 \
            --bind ${HOST}:${PORT} atfalsite.wsgi:application

# docker build . -f .docker/Dockerfile-web  -tatfal-web

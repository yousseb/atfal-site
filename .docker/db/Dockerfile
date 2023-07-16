FROM postgres:15-bookworm as base

LABEL version="1.0"
LABEL description="Reunite DB"

RUN set -ex; \
    apt-get update ; \
    apt-get install -y --no-install-recommends postgresql-15-repack autopostgresqlbackup libjemalloc2; \
    rm -rf /var/lib/apt/lists/*;

# better memory allocation
ENV LD_PRELOAD=/usr/lib/aarch64-linux-gnu/libjemalloc.so.2

# docker build .  -tatfal-db

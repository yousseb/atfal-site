FROM debian:bookworm-slim

LABEL version="1.0"
LABEL description="Reunite nginx image"

ARG DEBIAN_FRONTEND=noninteractive

RUN set -ex; \
    apt-get update && \
    apt-get -qq install curl locales libjemalloc2 ca-certificates tzdata libopenblas0 \
             nginx-full cron python3-certbot-nginx  && \
    rm -rf /var/lib/apt/lists/*


# better memory allocation
ENV LD_PRELOAD=/usr/lib/aarch64-linux-gnu/libjemalloc.so.2

VOLUME /etc/nginx

EXPOSE 80
EXPOSE 443

CMD ["nginx", "-g", "daemon off;"]

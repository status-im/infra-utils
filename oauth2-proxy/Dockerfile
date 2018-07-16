FROM alpine:3.8

ENV GOLANG_VERSION=1.8.1

ENV OAUTH2_PROXY_SHORT_VERSION=2.2
ENV OAUTH2_PROXY_VERSION=2.2.0
ENV OAUTH2_ARCHIVE=oauth2_proxy-$OAUTH2_PROXY_VERSION.linux-amd64.go$GOLANG_VERSION
ENV OAUTH2_ARCHIVE_SHA256=1c16698ed0c85aa47aeb80e608f723835d9d1a8b98bd9ae36a514826b3acce56
ENV OAUTH2_URL=https://github.com/bitly/oauth2_proxy/releases/download/v$OAUTH2_PROXY_SHORT_VERSION/$OAUTH2_ARCHIVE.tar.gz

# Deps
RUN apk add --no-cache ca-certificates && \
    apk add --no-cache --virtual curl gettext

WORKDIR /tmp

RUN curl -sL -o oauth2_proxy.tar.gz "$OAUTH2_URL" && \
    echo "$OAUTH2_ARCHIVE_SHA256  oauth2_proxy.tar.gz" | sha256sum -c && \
    tar xzvf oauth2_proxy.tar.gz && \
    cp $OAUTH2_ARCHIVE/oauth2_proxy /bin && \
    chmod +x /bin/oauth2_proxy

# Cleanup
RUN rm -fr /tmp/oauth2*

# Default settings
ENV OAUTH2_COOKIE_EXPIRE=24h \
    OAUTH2_COOKIE_HTTPONLY=false \
    OAUTH2_COOKIE_REFRESH=1h \
    OAUTH2_COOKIE_SECURE=false \
    OAUTH2_EMAIL_DOMAINS=["*"] \
    OAUTH2_HTTP_ADDRESS=127.0.0.1:8090 \
    OAUTH2_PROVIDER=github \
    OAUTH2_REQUEST_LOGGING=false

# Mandatory settings
ENV OAUTH2_CLIENT_ID= \
    OAUTH2_CLIENT_SECRET= \
    OAUTH2_COOKIE_DOMAIN= \
    OAUTH2_COOKIE_SECRET= \
    OAUTH2_REDIRECT_URL= \
    OAUTH2_UPSTREAMS=

ADD oauth2.cfg.tpl /var/lib/oauth.cfg.tpl
ADD entrypoint.sh /entrypoint.sh

ENTRYPOINT ["/bin/oauth2_proxy"]

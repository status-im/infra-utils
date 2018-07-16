FROM alpine:3.8

ENV GOLANG_VERSION=1.8.1

ENV OAUTH2_PROXY_SHORT_VERSION=2.2
ENV OAUTH2_PROXY_VERSION=2.2.0
ENV OAUTH2_ARCHIVE=oauth2_proxy-$OAUTH2_PROXY_VERSION.linux-amd64.go$GOLANG_VERSION
ENV OAUTH2_ARCHIVE_SHA256=1c16698ed0c85aa47aeb80e608f723835d9d1a8b98bd9ae36a514826b3acce56
ENV OAUTH2_URL=https://github.com/bitly/oauth2_proxy/releases/download/v$OAUTH2_PROXY_SHORT_VERSION/$OAUTH2_ARCHIVE.tar.gz

# Deps
RUN apk add --no-cache ca-certificates gettext curl 

WORKDIR /tmp

RUN curl -sL -o oauth2_proxy.tar.gz "$OAUTH2_URL" && \
    echo "$OAUTH2_ARCHIVE_SHA256  oauth2_proxy.tar.gz" | sha256sum -c && \
    tar xzvf oauth2_proxy.tar.gz && \
    cp $OAUTH2_ARCHIVE/oauth2_proxy /bin && \
    chmod +x /bin/oauth2_proxy

# Cleanup
RUN rm -fr /tmp/oauth2*

ENTRYPOINT ["/bin/oauth2_proxy"]

FROM yondon/livepeer-ubuntu1604:latest
MAINTAINER Jakub Sokolowski "jakub@status.im"

LABEL description="Go implementation of the Livepeer protocol in Docker form"

ARG LIVEPEER_VERSION
ENV LIVEPEER_URL https://github.com/livepeer/go-livepeer/releases/download
ENV LIVEPEER_ARCHIVE livepeer_linux.tar.gz

RUN apt-get update && apt-get -y install curl && \
    apt-get clean && rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*

RUN cd /tmp && \
    curl -sOL ${LIVEPEER_URL}/${LIVEPEER_VERSION}/${LIVEPEER_ARCHIVE} && \
    tar xvf ${LIVEPEER_ARCHIVE} && \
    mv livepeer_linux/* /usr/bin/ && \
    rm -r ${LIVEPEER_ARCHIVE} livepeer_linux

# folder for LivePeer data
VOLUME /root/.lpData

WORKDIR /tmp
ENTRYPOINT ["/usr/bin/livepeer"]
CMD ["--help"]

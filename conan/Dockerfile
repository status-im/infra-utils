FROM python:alpine
MAINTAINER Jakub Sokołowski <jakub@status.im>

ENV CONAN_PORT 9300
ENV CONAN_WORKERS 4
ENV CONAN_TIMEOUT 300

ARG CONAN_VERSION
ARG GUNICORN_VERSION

# Install dependencies so they get cached with the image
VOLUME /var/lib/conan
RUN apk update && \
    apk add musl-dev gcc && \
    pip install --no-cache-dir \
        conan==${CONAN_VERSION} \
        gunicorn==${GUNICORN_VERSION}

# Run uwsgi listening on port 9300
EXPOSE ${CONAN_PORT}

LABEL source="https://github.com/status-im/infra-utils"
LABEL description="Conan server repository service"
LABEL maintainer="jakub@status.im"

WORKDIR /var/lib/conan

COPY ./entrypoint.sh /entrypoint.sh
CMD ["/bin/sh", "/entrypoint.sh"]

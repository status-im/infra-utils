FROM node:12.15-alpine3.11

ARG WEBRTC_VERSION

ENV PORT=9090 \
    HOST=0.0.0.0

RUN apk update \
 && apk add --no-cache git \
 && yarn global add libp2p-webrtc-star@${WEBRTC_VERSION} \
 && yarn cache clean \
 && apk del git

LABEL source="https://github.com/status-im/infra-utils" \
      description="libp2p WebRTC transport that includes a discovery mechanism provided by the signalling-star" \
      maintainer="jakub@status.im"

CMD ["/usr/local/bin/star-signal"]
EXPOSE $PORT

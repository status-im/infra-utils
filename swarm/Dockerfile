FROM alpine:3.8 as builder

ENV GOLANG_VERSION=1.10.3
ENV ETHEREUM_REPO=https://github.com/ethereum/go-ethereum

# Deps
RUN apk add --no-cache git make go linux-headers gcc musl-dev 
ENV GOPATH=/go/

RUN mkdir -p "${GOPATH}/src/github.com/ethereum" && \
    git clone "$ETHEREUM_REPO" "${GOPATH}/src/github.com/ethereum/go-ethereum"

WORKDIR "${GOPATH}/src/github.com/ethereum/go-ethereum"

RUN go get github.com/ethereum/go-ethereum
RUN go install ./cmd/geth
RUN go install ./cmd/swarm

# Copy the binary to the second image
FROM alpine:latest

LABEL source="https://github.com/status-im/infra-utils"
LABEL description="Swarm docker image created for Status.im"
LABEL maintainer="support@status.im"

COPY --from=builder /go/bin/geth /bin/geth
COPY --from=builder /go/bin/swarm /bin/swarm

ENTRYPOINT ["/bin/swarm"]
CMD ["--help"]

EXPOSE 30399

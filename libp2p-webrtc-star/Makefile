WEBRTC_VERSION = v0.17.6

IMAGE_TAG = $(WEBRTC_VERSION)
IMAGE_NAME = statusteam/libp2p-webrtc-star:$(IMAGE_TAG)

build:
	docker build \
		--build-arg="WEBRTC_VERSION=$(WEBRTC_VERSION)" \
		-t $(IMAGE_NAME) .

push: build
	docker push $(IMAGE_NAME)

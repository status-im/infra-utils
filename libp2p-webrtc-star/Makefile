IMAGE_TAG = latest
IMAGE_NAME = statusteam/libp2p-webrtc-star:$(IMAGE_TAG)

build:
	docker build \
		--build-arg="LIVEPEER_VERSION=$(LIVEPEER_VERSION)" \
		-t $(IMAGE_NAME) .

push: build
	docker push $(IMAGE_NAME)

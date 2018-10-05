LIVEPEER_VERSION = 0.3.1

IMAGE_TAG = ubuntu
IMAGE_NAME = statusteam/livepeer:$(IMAGE_TAG)

build:
	docker build \
		--build-arg="LIVEPEER_VERSION=$(LIVEPEER_VERSION)" \
		-t $(IMAGE_NAME) .

push: build
	docker push $(IMAGE_NAME)

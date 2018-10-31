CONAN_VERSION = 1.9.0
GUNICORN_VERSION = 19.9.0

IMAGE_TAG = latest
IMAGE_NAME = statusteam/conan:$(IMAGE_TAG)

build:
	docker build \
		--build-arg="CONAN_VERSION=$(CONAN_VERSION)" \
		--build-arg="GUNICORN_VERSION=$(GUNICORN_VERSION)" \
		-t $(IMAGE_NAME) .

push: build
	docker push $(IMAGE_NAME)

NIX_VERSION = 2.2.1
JENKINS_UID = 1001
JENKINS_GID = 1001

IMAGE_TAG = jenkins
IMAGE_NAME = statusteam/nix:$(IMAGE_TAG)

build:
	docker build \
		--build-arg="JENKINS_UID=$(JENKINS_UID)" \
		--build-arg="JENKINS_GID=$(JENKINS_GID)" \
		--build-arg="NIX_VERSION=$(NIX_VERSION)" \
		-t $(IMAGE_NAME) .

push: build
	docker push $(IMAGE_NAME)

JENKINS_UID = 1001
JENKINS_GID = 1001

NIX_VERSION = 2.2.1
NIX_INSTALL = nix-install-$(NIX_VERSION).sh
NIX_SHA = 0039df605d2324f721f0c99ab76fc58fa60f791d84b30196eed805e8e65b1e51
NIX_URL = https://nixos.org/releases/nix/nix-$(NIX_VERSION)/install

IMAGE_TAG = ubuntu
IMAGE_NAME = statusteam/nix:$(IMAGE_TAG)

build: $(NIX_INSTALL)
	docker build \
		--build-arg="JENKINS_UID=$(JENKINS_UID)" \
		--build-arg="JENKINS_GID=$(JENKINS_GID)" \
		--build-arg="NIX_VERSION=$(NIX_VERSION)" \
		-t $(IMAGE_NAME) .

$(NIX_INSTALL):
	wget -q "$(NIX_URL)" -O "$(NIX_INSTALL)"
	echo "$(NIX_SHA)  $(NIX_INSTALL)" | sha256sum --check
	chmod +x "$(NIX_INSTALL)"

push: build
	docker push $(IMAGE_NAME)

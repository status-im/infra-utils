.DEFAULT_GOAL := all

all: oauth2-proxy-image

oauth2-proxy-image: ## Build the oauth2-proxy docker container
	docker build oauth2-proxy --tag statusteam/oauth2-proxy:2.2.0

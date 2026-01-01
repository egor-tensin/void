include prelude.mk

PORT ?= 23666
$(eval $(call noexpand,PORT))

URL := http://localhost:$(PORT)/
STATE := ./void.state

.PHONY: all
all: serve

.PHONY: serve
serve:
	./server.py --port '$(call escape,$(PORT))' --void '$(call escape,$(STATE))'

.PHONY: clean
clean:
	rm -f -- '$(call escape,$(STATE))'

.PHONY: view
view:
	xdg-open '$(call escape,$(URL))' &> /dev/null

.PHONY: test
test:
	./test/test.sh

.PHONY: build
build: docker/build

.PHONY: docker/build
docker/build:
	docker compose build --progress plain --pull

.PHONY: docker/serve
docker/serve: build/docker
	docker compose up

.PHONY: deploy
deploy: docker/build
	docker compose up -d

.PHONY: undeploy
undeploy:
	docker compose down --rmi all --volumes

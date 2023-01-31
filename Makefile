MAKEFLAGS += --no-builtin-rules --no-builtin-variables --warn-undefined-variables
unexport MAKEFLAGS
.DEFAULT_GOAL := all
.DELETE_ON_ERROR:
.SUFFIXES:
SHELL := bash
.SHELLFLAGS := -eu -o pipefail -c

escape = $(subst ','\'',$(1))

define noexpand
ifeq ($$(origin $(1)),environment)
    $(1) := $$(value $(1))
endif
ifeq ($$(origin $(1)),environment override)
    $(1) := $$(value $(1))
endif
ifeq ($$(origin $(1)),command line)
    override $(1) := $$(value $(1))
endif
endef

.PHONY: all
all: serve

PORT ?= 23666
$(eval $(call noexpand,PORT))

URL := http://localhost:$(PORT)/
STATE := ./void.state

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

DOCKER_HOST ?= unix:///var/run/docker.sock
$(eval $(call noexpand,DOCKER_HOST))
export DOCKER_HOST

.PHONY: build/docker
build/docker:
	docker-compose pull
	docker-compose build --pull

.PHONY: serve/docker
serve/docker: build/docker
	docker-compose up

.PHONY: deploy
deploy: docker-build
	docker-compose up -d

.PHONY: undeploy
undeploy:
	docker-compose down --rmi all --volumes

include prelude.mk

PORT ?= 23666
$(eval $(call noexpand,PORT))

url := http://localhost:$(PORT)/
state := ./void.state

venv_dir := .venv
venv_activate := . '$(call escape,$(venv_dir)/bin/activate)'

.PHONY: all
all: serve

.PHONY: venv/reset
venv/reset:
	rm -rf -- '$(call escape,$(venv_dir))'
	mkdir -p -- '$(call escape,$(venv_dir))'
	python -m venv -- '$(call escape,$(venv_dir))'

.PHONY: venv
venv: venv/reset
	$(venv_activate) && pip install -q -r requirements.txt

.PHONY: serve
serve:
	$(venv_activate) && ./server.py --port '$(call escape,$(PORT))' --void '$(call escape,$(state))'

.PHONY: clean
clean:
	rm -f -- '$(call escape,$(state))'

.PHONY: view
view:
	xdg-open '$(call escape,$(url))' &> /dev/null

.PHONY: test
test:
	./test/test.sh

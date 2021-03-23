.PHONY: clean virtualenv test install

PYTHON_PATH := $(shell which python3)

test:
	@echo $(PYTHON_PATH)

clean:
	find . -name '*.py[co]' -delete

virtualenv:
	virtualenv --python="$(PYTHON_PATH)" --prompt=="|> BGPFSM <|" src/env
	src/env/bin/pip3 install -r src/requirements.txt
	source src/env/bin/activate
	pip3 freeze | sed -ne 's/==.*//p' | xargs ${ENV_NAME}/bin/pip3 install -U
	deactivate
	@echo
	@echo "Virtualenv created, use 'source src/env/bin/activate' to use it"
	@echo

install:
	sudo apt-get -y install python-virtualenv parallel graphviz gcc python3-dev

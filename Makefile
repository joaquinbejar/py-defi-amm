export PATH := /app/.local/bin:$(PATH)
FLASK_APP := src/defi_amm/main.py
PYINSTALLER := pyinstaller
VENV_NAME?=venv
VENV_ACTIVATE=$(VENV_NAME)/bin/activate
PYTHON_PATH=$(shell which python3.11)

create-venv: delete-venv
	$(PYTHON_PATH) -m venv $(VENV_NAME)
	@echo "To activate the venv, run 'source $(VENV_ACTIVATE)'"

delete-venv:
	rm -rf venv

uninstall:
	pip uninstall -y defi_amm

clean-build-and-dist:
	rm -rf ./build
	rm -rf ./dist
	rm -rf defi_amm.egg-info

build: clean-build-and-dist update-pip
	pip install build
	python -m build --wheel --sdist

clean :
	rm -rf build/
	rm -rf *.egg-info

reinstall-dependencies: update-pip delete-dependencies install-dep clean

update-pip:
	$(PYTHON_PATH) --version
	$(PYTHON_PATH) -m pip install --upgrade pip --no-cache-dir
	$(PYTHON_PATH) -m pip install pip~=23.2.1 --force-reinstall --no-cache-dir
	pip install --upgrade pip


delete-dependencies:
	pip freeze | xargs -I %v pip uninstall -y '%v'

docker-build:
	docker build -f Docker/Dockerfile -t "defi_amm:latest" .

docker-run: docker-build
	docker run -p 5000:5000 --name defi_amm defi_amm:latest

### ***** UNIT TESTS ***** ###

run-unit-test-coverage:
	coverage run --source=defi_amm -m unittest discover -v -s ./tests/unit/ -p '*test*.py'
	coverage report
	coverage html -d coverage_html
	echo report at '$(COVERAGE_LOCATION)'

run-unit-tests:		## Run unit tests
	python -m unittest discover -v -s ./tests/unit/ -p '*test*.py'

### ***** CI PIPELINE ***** ###

install-dep:	## Install dependencies
	pip install .

test:		## Run tests
	pip install pytest mockito coverage freezegun pytest-cov
	pip install .[tests]
	coverage run --source=src -m pytest tests/unit/ && coverage report -m


test_unittest:		## Run tests
	pip install mockito freezegun coverage
	pip install .[tests]
	coverage erase
	PYTHONDONTWRITEBYTECODE=1 coverage run --source=src/defi_amm/ -m unittest discover -s tests/unit/ -p "test_*.py"
	coverage report -m


### ***** BUILD EXECUTABLE ***** ###
create-executable:
	$(PYINSTALLER) --onefile $(FLASK_APP)
	@echo "Executable created in the 'dist' directory"
##  This is the build file containing all targets to be build based on
##  optional dependencies and action encapsulated by them

# Variables scope
VENV = virtual
VENV_DIR = ./$(VENV)
PYTHON = $(VENV_DIR)/bin/python3
PIP = $(VENV_DIR)/bin/pip3
PROJECT_NAME := stravaAPI


.PHONY: virtual install source_dist clean

# Targets
virtual:
	python3 -m venv $(VENV)

install: install_req install_edit

install_req: virtual
	$(PIP) install -r requirements.txt

install_edit: virtual
	$(PYTHON) -m pip install .

source_dist: virtual
	$(PYTHON) setup.py sdist --formats=zip

clean: clean.venv clean.dist

clean.venv:
	rm -rf $(VENV)

clean.dist:
	rm -rf dist
	rm -rf *.egg-info
	rm -rf build

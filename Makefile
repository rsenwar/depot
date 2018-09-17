PROJ=depot
PYTHON=python
PYTHON3=python3
PYDOCSTYLE=pydocstyle
ICONV=iconv
SPHINX2RST=sphinx2rst
RST2HTML=rst2html.py
DEVNULL=/dev/null

TESTDIR=depot/tests

SPHINX_DIR=depot/docs/code
SPHINX_BUILDDIR=${SPHINX_DIR}/_build
SPHINX_SOURCEDIR=${SPHINX_DIR}
SPHINX_HTMLDIR=${SPHINX_BUILDDIR}/html
DOCUMENTATION=depot/docs/Documentation
README=README.rst
README_SRC=depot/docs/readme.txt
DOCKER_IMAGE_NAME=${PROJ}:latest

.PHONY: help bootstrap runserver clean test lint readme flakes docker readme coverage

all: help

clean-docs:
		rm -rf "$(SPHINX_BUILDDIR)" "$(DOCUMENTATION)"

clean-pyc:
		find . -type f -a \( -name "*.pyc" -o -name "*$$py.class" \) | xargs rm
		find . -type d -name "__pycache__" | xargs rm -r

clean-build:
		rm -rf build/ dist/ .eggs/ *.egg-info/

clean-test:
		rm -rf .tox/ .coverage htmlcov/

bump:
		@echo $(JIRA_ID)
		bumpversion patch
		-$(MAKE) catversion

bump-minor:
		@echo "JIRA ID -" ${JIRA_ID}
		bumpversion minor
		-$(MAKE) catversion

bump-major:
		@echo "JIRA ID -" ${JIRA_ID}
		bumpversion major
		-$(MAKE) catversion

flakecheck:
		flake8 "$(PROJ)"

pep257check:
		$(PYDOCSTYLE) "$(PROJ)"

Documentation:
		(cd "$(SPHINX_DIR)"; $(MAKE) apidoc; $(MAKE) html)
		mv "$(SPHINX_HTMLDIR)" $(DOCUMENTATION)
		@echo "The HTML pages are in " $(DOCUMENTATION)
		@open $(DOCUMENTATION)/index.html

pytestcheck:
		py.test -xv "$(PROJ)"

pylintcheck:
		(cd $(PROJ); pylint "$(PROJ)")

readmecheck-unicode:
		$(ICONV) -f ascii -t ascii $(README) >/dev/null

readmecheck-rst:
		-$(RST2HTML) $(README) >$(DEVNULL)

readmecheck: readmecheck-unicode readmecheck-rst

$(README):
	$(SPHINX2RST) "$(README_SRC)" --ascii > $@

readme: clean-readme $(README) readmecheck

clean-readme:
		-rm -f $(README)

catversion:
		-cat config/VERSION
		-$(MAKE) latest-tag

latest-tag:
		git describe --tags


help:
	@echo "bootstrap              - Setup the local environment."
	@echo "runserver              - Python django runserver @ port 8009."
	@echo "docs                   - Build Documentation."
	@echo "coverage               - Show coverage of tests."
	@echo "readme                 - Regenerate README.rst file."
	@echo "test                   - Run unittests using current python."
	@echo "   pytestcheck         - Run pytest using current python."
	@echo "   lint ------------   - Check codebase for problems."
	@echo "     readmecheck       - Check README.rst encoding."
	@echo "     flakes --------   - Check code for syntax and style errors."
	@echo "        flakecheck     - Run flake8 on the source code."
	@echo "        pylintcheck    - Run pylint on the source code."
	@echo "        pep257check    - Run pep257 on the source code."
	@echo "clean --------------   - Non-destructive clean"
	@echo "    clean-pyc          - Remove .pyc/__pycache__ files."
	@echo "    clean-docs         - Remove documentation build artifacts."
	@echo "    clean-build        - Remove setup artifacts."
	@echo "    clean-test         - Remove test and coverage artifacts."
	@echo "bump                   - Bump patch version number."
	@echo "bump-minor             - Bump minor version number."
	@echo "bump-major             - Bump major version number."
	@echo "catversion             - Print the current version number."
	@echo "latest-tag             - Print the latest tag."
	@echo "docker -------------   - Build and run the docker image"
	@echo "    docker-build       - Build docker image."
	@echo "    docker-run         - run the built docker image."
	@echo "dc-dev-build           - Docker new image build and run with docker-compose."
	@echo "dc-dev-up              - Docker image build and run with docker-compose."
	@echo "add-git-hooks          - Add git hooks to your .git configs."


bootstrap:
		python3 -m venv venv_depot
		(. venv_depot/bin/activate; pip install -r config/pip/requirements_dev.txt)
		cp depot/depot_proj/settings/local.py.dist depot/depot_proj/settings/local.py
		cp depot/depot_proj/settings/dev.py.dist depot/depot_proj/settings/dev.py

runserver:
		( \
			source venv_depot/bin/activate; \
			python depot/manage_local.py runserver 8009 \
		)

clean: clean-docs clean-pyc clean-build clean-test

test: pytestcheck lint

lint: readmecheck flakes

flakes: flakecheck pep257check pylintcheck

docker-build:
		docker build --build-arg DEPOT_BUILD_ENV=dev -t $(DOCKER_IMAGE_NAME) .

docker-run:
		docker run -p 8089:80 -it -e CURR_ENV=dev -d $(DOCKER_IMAGE_NAME)

docker: docker-build docker-run

dc-dev-build:
		docker-compose -f config/docker-compose/dev.yml build

dc-dev-up:
		docker-compose -f config/docker-compose/dev.yml up -d

coverage: pytestcheck
		@coverage report -m
		@coverage html
		@open htmlcov/index.html

docs: clean-docs Documentation

add-git-hooks:
		@cp config/git/hooks/* .git/hooks/





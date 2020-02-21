help:
	@echo "clean - remove all build, test, coverage and Python artifacts"
	@echo "clean-build - remove build artifacts"
	@echo "clean-pyc - remove Python file artifacts"
	@echo "install - install the package to the active Python's site-packages"

pipenv:
	pip install pipenv
	pipenv install --dev

test:
	pipenv run flake8 pytube/
	pipenv run flake8 tests/
	pipenv run black pytube --check
	pipenv run black tests --check
	pipenv run mypy pytube
	pipenv run pytest --cov-report term-missing --cov=pytube

ci: pipenv test

clean: clean-build clean-pyc

clean-build:
	rm -fr build/
	rm -fr dist/
	rm -fr .eggs/
	find . -name '*.egg-info' -exec rm -fr {} +
	find . -name '*.egg' -exec rm -f {} +
	find . -name '*.DS_Store' -exec rm -f {} +

clean-pyc:
	find . -name '*.pyc' -exec rm -f {} +
	find . -name '*.pyo' -exec rm -f {} +
	find . -name '*~' -exec rm -f {} +
	find . -name '__pycache__' -exec rm -fr {} +
	find . -name '.pytest_cache' -exec rm -fr {} +
	find . -name '.mypy_cache' -exec rm -fr {} +

install: clean
	python setup.py install

package: clean
	pipenv run python setup.py sdist bdist_wheel

upload:
	twine upload dist/*

tag:
	git diff-index --quiet HEAD --  # checks for unstaged/uncomitted files
	git tag "v`pipenv run python pytube/version.py`"
	git push --tags

check-master:
	if [[ `git rev-parse --abbrev-ref HEAD` != "master" ]]; then exit 1; fi

pull:
	git pull

release: check-master pull clean test tag package upload

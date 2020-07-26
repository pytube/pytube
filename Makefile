dev:
	pipenv install --dev

pipenv:
	pip install pipenv
	pipenv install --dev

deploy-patch: clean requirements bumpversion-patch upload clean

deploy-minor: clean requirements bumpversion-minor upload clean

deploy-major: clean requirements bumpversion-major upload clean

requirements:
	pipenv_to_requirements

bumpversion-patch:
	bumpversion patch
	git push
	git push --tags

bumpversion-minor:
	bumpversion minor
	git push
	git push --tags

bumpversion-major:
	bumpversion major
	git push
	git push --tags

upload:
	python setup.py sdist bdist_wheel
	twine upload dist/*

help:
	@echo "clean - remove all build, test, coverage and Python artifacts"
	@echo "clean-build - remove build artifacts"
	@echo "clean-pyc - remove Python file artifacts"
	@echo "install - install the package to the active Python's site-packages"

ci:
	pip install pipenv
	pipenv install --dev --skip-lock
	pipenv run flake8
	# pipenv run pytest --cov-report term-missing # --cov=humps
	pipenv run coverage run -m pytest

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

install: clean
	python setup.py install

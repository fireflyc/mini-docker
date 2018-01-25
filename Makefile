PYTHON=python
PIPENV=pipenv

all: help

help:
	@echo "dev               -开发环境"
	@echo "dist              -发布"
	@echo "build             - 构建"
	@echo "clean             - 清理"

dev:
	$(PIPENV) shell

clean:
	find . -name "*.pyc" -print0 | xargs -0 rm -rf
	-rm -rf .coverage
	-rm -rf build
	-rm -rf dist
	-rm -rf *.egg-info

build:
	$(PYTHON) setup.py sdist

dist: clean build
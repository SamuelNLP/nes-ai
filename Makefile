-include .env

SHELL = /bin/bash
PACKAGE_VERSION:=$(shell git describe --tags --abbrev=0)

clean_dist:
	rm -rf dist *.egg-info

clean_tests:
	rm -rf .pytest_cache .tox .coverage htmlcov
	py3clean .

clean_mypy:
	rm -rf .mypy_cache

clean_ruff:
	rm -rf .ruff_cache

clean: clean_dist clean_mypy clean_tests clean_ruff

test:
	uv run pytest -v -p no:cacheprovider tests

test_w_coverage:
	uv run pytest -v --cov-report html --cov=nes_ai tests/ #--cov-fail-under=90

package: clean_dist
	uv build --format wheel

mypy:
	uv run mypy .

ruff:
	uv run ruff format .
	uv run ruff check . --fix

install_reqs:
	uv pip install git+ssh://git@github.com/SamuelNLP/neats.git@3.1.0
	uv pip install git+https://github.com/SamuelNLP/PyGame-Learning-Environment.git

benchmark:
	cp scripts/benchmarks/benchmark_super_mario.py .
	kernprof -l benchmark_super_mario.py
	python -m line_profiler benchmark_super_mario.py.lprof
	rm benchmark_super_mario.*

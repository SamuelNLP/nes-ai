# some common operations

clean_dist:
	rm -rf dist *.egg-info

clean_tests:
	rm -rf .pytest_cache .tox
	py3clean .

clean_mypy:
	rm -rf .mypy_cache

clean_benchmark:
	rm -f temp.stats

clean: clean_dist clean_mypy clean_tests clean_benchmark

test:
	tox

package: clean_dist
	python setup.py sdist

vulture:
	vulture nes_ai/

mypy:
	mypy . --ignore-missing-imports

flake8:
	flake8 .

format:
	isort .
	black .

export_reqs:
	pip-chill --no-version > requirements.txt
	sed -i '/ple/d' requirements.txt

install_reqs:
	pip install pip wheel --upgrade
	pip install git+ssh://git@github.com/SamuelNLP/neats.git@3.0.0
	pip install git+https://github.com/SamuelNLP/PyGame-Learning-Environment.git
	pip install -r requirements.txt --upgrade

clean_pip:
	pip uninstall ple -y
	pip freeze | xargs pip uninstall -y

reinstall_pip: clean_pip install_reqs

benchmark:
	cp scripts/benchmarks/benchmark_super_mario.py .
	kernprof -l benchmark_super_mario.py
	python -m line_profiler benchmark_super_mario.py.lprof
	rm benchmark_super_mario.*

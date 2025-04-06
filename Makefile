install:
	pip install -e .[dev]

lint:
	black src
	flake8 src

run:
	python main.py

clean:
	rm -rf build dist *.egg-info

format:
	isort src
	black src

build:
	python -m build

publish:
	twine upload dist/*
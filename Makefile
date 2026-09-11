.PHONY: install dev build clean test

install:
    pip install .

dev:
    pip install -e . pytest

build:
    python -m pip install --upgrade build
    python -m build

test:
    pytest -q

clean:
    rm -rf build dist src/project_tree.egg-info .pytest_cache
    find . -type d -name __pycache__ -prune -exec rm -rf {} +
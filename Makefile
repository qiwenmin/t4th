.PHONY: test test-standard coverage run

test:
	python -m unittest discover -s tests

test-standard:
	@echo "include tests/ttester.fs include tests/test_core.fs" | python main.py

coverage:
	python -m coverage run -m unittest discover -s tests
	python -m coverage report

run:
	python main.py

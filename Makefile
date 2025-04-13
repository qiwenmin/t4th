.PHONY: test test-standard

FS_TESTS := $(wildcard tests/test_*.fs)

test:
	python -m unittest discover -s tests

test-standard:
	@(cat tests/ttester.fs; echo ; cat $(FS_TESTS)) | python main.py

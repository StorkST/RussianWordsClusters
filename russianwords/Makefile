python := python3.8
test_dir := tests/

test: test-words test-wordpairs

test-words:
	$(python) $(test_dir)test_words.py

test-wordpairs:
	$(python) $(test_dir)test_wordpairs.py

test-notmerge:
	$(python) $(test_dir)test_words.py tests/words/not-merge/*

updatePypi:
	cd .. && python3.8 setup.py sdist bdist_wheel && python3.8 -m twine upload dist/* && rm -rf dist/*

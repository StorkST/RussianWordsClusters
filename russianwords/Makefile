python := python3.8
test_dir := tests/

test:
	$(python) $(test_dir)test_words.py
	$(python) $(test_dir)test_wordpairs.py

updatePypi:
	cd .. && python3.8 setup.py sdist bdist_wheel && python3.8 -m twine upload dist/* && rm -rf dist/*

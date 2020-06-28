python := python3.8
test_dir := tests/

test:
	$(python) $(test_dir)test_words.py
	$(python) $(test_dir)test_wordpairs.py

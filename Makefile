test:
	python3 webplay.py <test/test.txt -c test.css -s test.js >test/test.html

lint:
	black webplay.py
	mypy --strict webplay.py
	pylint webplay.py

clean:
	rm -f test/test.html

.PHONY: test lint clean


all:
	python -m compileall -f EnsEMBL REST Utils 

test:
	python -m unittest discover -s ./test -p 'test_*.py' -vv

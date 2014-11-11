
#To redo-test if date timestamps haven't been updated
.PHONY: all test clean

all:
	python -m compileall -f EnsEMBL REST Utils 

test:
	cd test; python -m unittest discover -s ./ -p 'test_*.py' -vv

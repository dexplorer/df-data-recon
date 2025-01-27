install: requirements.txt
	pip install --upgrade pip &&\
	pip install -r requirements.txt

setup: 
	python setup.py install

lint:
	pylint --disable=R,C *.py &&\
	pylint --disable=R,C dr_app/*.py &&\
	pylint --disable=R,C dr_app/tests/*.py

test:
	python -m pytest -vv --cov=dr_app dr_app/tests

format:
	black *.py &&\
	black dr_app/*.py &&\
	black dr_app/tests/*.py

all:
	install setup lint format test

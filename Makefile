.PHONY: clean test codestyle  

clean:
	find bndl_elastic -name '*.pyc' -exec rm -f {} +
	find bndl_elastic -name '*.pyo' -exec rm -f {} +
	find bndl_elastic -name '*.c' -exec rm -f {} +
	find bndl_elastic -name '*.so' -exec rm -f {} +
	find bndl_elastic -name '*~' -exec rm -f {} +
	find bndl_elastic -name '__pycache__' -exec rm -rf {} +
	rm -rf build
	rm -rf dist
	rm -rf .coverage .coverage.* htmlcov

test:
	rm -fr .coverage .coverage.* htmlcov
	BNDL_SUPERVISOR_ONSIGTERM=raise_exit \
	COVERAGE_PROCESS_START=.coveragerc \
	coverage run -m pytest bndl_elastic
	coverage combine
	coverage html

codestyle:
	pylint bndl_elastic > build/pylint.html
	flake8 bndl_elastic > build/flake8.txt

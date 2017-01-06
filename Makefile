ELASTIC_VERSION ?= 5.1.1

ELASTIC_VERSION_MAJOR = $(word 1,$(subst ., ,$(ELASTIC_VERSION)))

ifeq ('$(ELASTIC_VERSION_MAJOR)', '5')
	ELASTIC_URL = https://artifacts.elastic.co/downloads/elasticsearch/elasticsearch-$(ELASTIC_VERSION).tar.gz
endif

ifeq ('$(ELASTIC_VERSION_MAJOR)', '2')
	ELASTIC_URL = https://download.elastic.co/elasticsearch/release/org/elasticsearch/distribution/tar/elasticsearch/$(ELASTIC_VERSION)/elasticsearch-$(ELASTIC_VERSION).tar.gz
endif

ifeq ('$(ELASTIC_VERSION_MAJOR)', '1')
	ELASTIC_URL = https://download.elastic.co/elasticsearch/elasticsearch/elasticsearch-$(ELASTIC_VERSION).tar.gz
endif


.PHONY: clean test codestyle install-elastic start-elastic stop-elastic

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
	COVERAGE_PROCESS_START=.coveragerc \
	coverage run -m pytest --junitxml build/junit.xml bndl_elastic
	coverage combine
	coverage html -d build/htmlcov
	coverage xml -o build/coverage.xml

codestyle:
	pylint bndl_elastic > build/pylint.log || :
	flake8 bndl_elastic > build/flake8.txt || :


install-elastic:
	pip install "elasticsearch>=$(ELASTIC_VERSION_MAJOR),<$(shell expr $(ELASTIC_VERSION_MAJOR) + 1)"
	mkdir -p /tmp/elasticsearch
	cd /tmp/elasticsearch ; test -d $(ELASTIC_VERSION) || \
		(curl $(ELASTIC_URL) | tar xz && mv elasticsearch-$(ELASTIC_VERSION) $(ELASTIC_VERSION))

start-elastic: stop-elastic install-elastic
	nohup /tmp/elasticsearch/$(ELASTIC_VERSION)/bin/elasticsearch > /tmp/elasticsearch/elastic.log 2>&1 & \
		echo $$! > /tmp/elasticsearch/elastic.pid
	while ! timeout 1 bash -c "echo > /dev/tcp/localhost/9200" > /dev/null 2>&1 ; do sleep 3 ; done

stop-elastic:
	test -f /tmp/elasticsearch/elastic.pid && kill `cat /tmp/elasticsearch/elastic.pid` || :
	test -f /tmp/elasticsearch/elastic.pid && rm /tmp/elasticsearch/elastic.pid || :


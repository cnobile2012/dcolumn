#
# Development by Carl J. Nobile
#
include include.mk

PREFIX		= $(shell pwd)
PACKAGE_DIR	= $(shell echo $${PWD\#\#*/})
APACHE_DIR	= $(PREFIX)/server
DOCS_DIR	= $(PREFIX)/docs
TODAY		= $(shell date +"%Y-%m-%d_%H%M")
RM_REGEX	= '(^.*.pyc$$)|(^.*.wsgic$$)|(^.*~$$)|(.*\#$$)|(^.*,cover$$)'
RM_CMD		= find $(PREFIX) -regextype posix-egrep -regex $(RM_REGEX) \
                  -exec rm {} \;
COVERAGE_DIR	= $(PREFIX)/.coverage_tests
COVERAGE_FILE	= .coveragerc
COVERAGE_PROCESS_START	= $(COVERAGE_FILE)
TEST_ARGS	= --parallel
PIP_ARGS	=

#----------------------------------------------------------------------
all	: tar

#----------------------------------------------------------------------
.PHONY	: tar
tar	: clean
	@(cd ..; tar -czvf $(PACKAGE_DIR).tar.gz --exclude=".git" \
          --exclude="example_site/static" $(PACKAGE_DIR))

.PHONY	: tests
tests	: clean
	@rm -rf $(DOCS_DIR)/htmlcov
	@coverage erase --rcfile=$(COVERAGE_FILE)
	@rm -rf $(COVERAGE_DIR)
	@mkdir -p $(COVERAGE_DIR)
	@coverage run --concurrency=multiprocessing \
         --rcfile=$(COVERAGE_FILE) ./manage.py test $(TEST_ARGS)
	@mv .coverage.* $(COVERAGE_DIR)
	@coverage combine --rcfile=$(COVERAGE_FILE) $(COVERAGE_DIR)
	@coverage report -m --rcfile=$(COVERAGE_FILE)
	@coverage html --rcfile=$(COVERAGE_FILE)

.PHONY	: sphinx
sphinx	: clean
	(cd $(DOCS_DIR); make html)

.PHONY	: gen-db-diagram
gen-db-diagram:
	@./manage.py graph_models -ago docs/realm_db.png

.PHONY	: build
build	: clean
	python setup.py sdist

.PHONY	: upload
upload	: clobber
	python setup.py sdist upload -r pypi

.PHONY	: upload-test
upload-test: clobber
	python setup.py sdist upload -r pypitest

.PHONY	: install-dev
install-dev:
	pip install $(PIP_ARGS) -r requirements/development.txt

#----------------------------------------------------------------------

.PHONY	: clean
clean	:
	$(shell $(RM_CMD))

.PHONY	: clobber
clobber	: clean
	@rm -rf dist build *.egg-info
	@rm -rf $(DOCS_DIR)/htmlcov
	@rm -rf $(DOCS_DIR)/build

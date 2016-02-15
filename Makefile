#
# Development by Carl J. Nobile
#

PREFIX		= $(shell pwd)
PACKAGE_DIR	= $(shell echo $${PWD\#\#*/})
APACHE_DIR	= $(PREFIX)/apache
DOCS_DIR	= $(PREFIX)/docs
TODAY		= $(shell date +"%Y-%m-%d_%H%M")

#----------------------------------------------------------------------
.PHONY	: all
all	: tar

#----------------------------------------------------------------------
.PHONY	: tar
tar	: clean
	@(cd ..; tar -czvf $(PACKAGE_DIR).tar.gz --exclude=".git" \
          --exclude="example_site/static" $(PACKAGE_DIR))

.PHONY	: api-docs
api-docs: clean
	@(cd $(DOCS_DIR); make)

.PHONY	: build
build	: clean
	python setup.py sdist

.PHONY	: upload
upload	: clobber
	python setup.py sdist upload -r pypi

.PHONY	: 
upload-test: clobber
	python setup.py sdist upload -r pypitest

#----------------------------------------------------------------------

.PHONY	: clean
clean	:
	$(shell cleanDirs.sh clean)

.PHONY	: clobber
clobber	: clean
	@rm -rf dist build *.egg-info
	@(cd $(DOCS_DIR); make clobber)

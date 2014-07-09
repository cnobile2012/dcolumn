#
# Development by Carl J. Nobile
#
# $Author: $
# $Date: $
# $Revision: $
#

PREFIX		= $(shell pwd)
PACKAGE_DIR	= $(shell echo $${PWD\#\#*/})
APACHE_DIR	= $(PREFIX)/apache
#DOCS_DIR	= $(PREFIX)/docs
#LOGS_DIR	= $(PREFIX)/logs
TODAY		= $(shell date +"%Y-%m-%d_%H%M")

#----------------------------------------------------------------------
all	: tar

#----------------------------------------------------------------------
tar	: clean
	@(cd ..; tar -czvf $(PACKAGE_DIR).tar.gz --exclude=".git" \
          --exclude="djangotests/static" --exclude=".DS_Store" $(PACKAGE_DIR))

build	: clean
	python setup.py sdist

#----------------------------------------------------------------------

clean	:
	$(shell cleanDirs.sh clean)

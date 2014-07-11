#
# docs/Makefile
#
# Development by Carl J. Nobile
#
# This Makefile generates the Dynamic Column API documtation.
#

FQDN		= $(shell hostname --fqdn)
DOC_DIR		= $(shell pwd)
API_DIR		= dcapi
URL		= http://${FQDN}${DOC_DIR}/${API_DIR}/index.html

# source setup_settings;

all	: clobber api-docs
#----------------------------------------------------------------------
api-docs:
	@(cd ..; \
          epydoc -v --name "Dynamic Columns" -o docs/${API_DIR} \
          --show-private --show-imports --graph all --url "${URL}" \
          */*.py */*/*.py */*/*/*.py  \
         )

#----------------------------------------------------------------------
clean	:
	@rm -f *~ \#* .\#*

clobber	: clean
	@rm -rf ${API_DIR}

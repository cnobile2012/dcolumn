#!/bin/bash

if [ "$#" -lt 1 ]; then
    printf "Must provide an environment i.e. dev, stg, prod\n"
    exit 1
fi

pg_dump --username=dcolumn -c --compress=9 dcolumn > db-snapshots/$1-$(date +"%Y%m%d%H%M").sql.gz

exit 0

#!/bin/bash

psql -h T24-DB -U t24 -d BANCA -t -A -c \
'SELECT COUNT(*) FROM "public"."F_OS_TOKEN";'

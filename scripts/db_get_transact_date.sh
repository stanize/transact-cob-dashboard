#!/bin/bash

psql -h T24-DB -U t24 -d BANCA -t -c \
"SELECT (xmlrecord::json)->>'1' FROM public.\"F_DATES\" WHERE recid='LU0010001';" | xargs

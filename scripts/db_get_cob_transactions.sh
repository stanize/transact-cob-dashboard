#!/bin/bash

psql -h T24-DB -U t24 -d BANCA -Atc "
SELECT split_part((xmlrecord::json)->>'19',' ',1)
FROM public.\"F_TSA_SERVICE\"
WHERE recid='COB';
"

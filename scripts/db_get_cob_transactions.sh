#!/bin/bash

psql -h T24-DB -U t24 -d BANCA -Atc "
SELECT ((xmlrecord::json)->'19')->>0
FROM public.\"F_TSA_SERVICE\"
WHERE recid='COB';
"

#!/bin/bash

set -euo pipefail

# ------------------------------------------------------------------------------
# db_get_cob_progress_json.sh
#
# Returns COB progress information from Transact PostgreSQL tables in JSON format
# so it can be consumed easily by Python / Streamlit.
#
# Optional environment variables:
#   DB_HOST       - PostgreSQL host
#   DB_PORT       - PostgreSQL port
#   DB_NAME       - PostgreSQL database name
#   DB_USER       - PostgreSQL username
#   COMPANY_ID    - Company / book id for COB date lookup in F_DATES
#
# Example:
#   DB_HOST=T24-DB DB_NAME=BANCA DB_USER=t24 COMPANY_ID=LU0010001 ./db_get_cob_progress_json.sh
# ------------------------------------------------------------------------------

DB_HOST="${DB_HOST:-T24-DB}"
DB_PORT="${DB_PORT:-5432}"
DB_NAME="${DB_NAME:-BANCA}"
DB_USER="${DB_USER:-t24}"
COMPANY_ID="${COMPANY_ID:-LU0010001}"

SQL=$(cat <<EOF
WITH stage_map AS (
    SELECT 'APPLICATION' AS stage, 'A' AS prefix, 1 AS sort_order
    UNION ALL SELECT 'SYSTEM WIDE', 'S', 2
    UNION ALL SELECT 'REPORTING', 'R', 3
    UNION ALL SELECT 'START OF DAY', 'D', 4
    UNION ALL SELECT 'ONLINE', 'O', 5
),
stage_counts AS (
    SELECT
        sm.stage,
        sm.sort_order,
        (
            SELECT COUNT(*)
            FROM public."F_BATCH" fb
            WHERE COALESCE((fb.xmlrecord::json)->>'1', '') LIKE sm.prefix || '%'
        ) AS total,
        (
            SELECT COUNT(*)
            FROM public."F_BATCH" fb
            WHERE COALESCE((fb.xmlrecord::json)->>'1', '') LIKE sm.prefix || '%'
              AND COALESCE((fb.xmlrecord::json)->>'3', '') = '2'
        ) AS processed
    FROM stage_map sm
),
stage_rows AS (
    SELECT
        stage,
        sort_order,
        processed,
        total,
        CASE
            WHEN total = 0 THEN 0
            ELSE ROUND((processed::numeric / total::numeric) * 100, 2)
        END AS pct_completed
    FROM stage_counts
),
overall_row AS (
    SELECT
        'COB' AS stage,
        6 AS sort_order,
        SUM(processed) AS processed,
        SUM(total) AS total,
        CASE
            WHEN SUM(total) = 0 THEN 0
            ELSE ROUND((SUM(processed)::numeric / SUM(total)::numeric) * 100, 2)
        END AS pct_completed
    FROM stage_rows
),
all_rows AS (
    SELECT * FROM stage_rows
    UNION ALL
    SELECT * FROM overall_row
),
cob_date_row AS (
    SELECT COALESCE((xmlrecord::json)->>'1', '') AS cob_date
    FROM public."F_DATES"
    WHERE recid = '${COMPANY_ID}'
    LIMIT 1
)
SELECT json_build_object(
    'system_time', to_char(CURRENT_TIMESTAMP, 'YYYY-MM-DD HH24:MI:SS'),
    'company_id', '${COMPANY_ID}',
    'cob_date', COALESCE((SELECT cob_date FROM cob_date_row), ''),
    'stages',
        (
            SELECT json_agg(
                json_build_object(
                    'stage', stage,
                    'processed', processed,
                    'total', total,
                    'pct_completed', pct_completed
                )
                ORDER BY sort_order
            )
            FROM all_rows
        )
);
EOF
)

psql \
  -h "$DB_HOST" \
  -p "$DB_PORT" \
  -U "$DB_USER" \
  -d "$DB_NAME" \
  -X \
  -q \
  -t \
  -A \
  -c "$SQL"

#!/bin/bash
set -e

# -------------------------------------------------------------------
# CineMind — container entrypoint
# 1. Wait for PostgreSQL to accept connections.
# 2. Run Alembic migrations.
# 3. Seed the movies table if it is empty.
# 4. Fall through to CMD (uvicorn / streamlit).
# -------------------------------------------------------------------

# ---- 1. Wait for PostgreSQL ----
echo "Waiting for PostgreSQL to be ready…"

timeout=60
elapsed=0
interval=2

while [ "$elapsed" -lt "$timeout" ]; do
    if python -c "
import os, psycopg
conn = psycopg.connect(os.environ['DATABASE_URL'])
conn.close()
" 2>/dev/null; then
        echo "PostgreSQL is ready!"
        break
    fi
    echo "PostgreSQL not ready yet… (${elapsed}s elapsed)"
    sleep "$interval"
    elapsed=$((elapsed + interval))
done

if [ "$elapsed" -ge "$timeout" ]; then
    echo "ERROR: PostgreSQL did not become ready within ${timeout}s."
    exit 1
fi

# ---- 2. Run Alembic migrations ----
# alembic.ini has a hardcoded local URL and a typo in script_location.
# We override both by generating a small runtime config in /tmp.
mkdir -p /tmp/alembic-rpc

cat > /tmp/alembic-rpc/alembic.ini << ALEMBIC_INI
[alembic]
script_location = /app/alembic
prepend_sys_path = /app
sqlalchemy.url = ${ALEMBIC_DATABASE_URL}
path_separator = os
target_metadata = cinemind.db.models.Base.metadata

[loggers]
keys = root,sqlalchemy,alembic

[handlers]
keys = console

[formatters]
keys = generic

[logger_root]
level = WARNING
handlers = console
qualname =

[logger_sqlalchemy]
level = WARNING
handlers =
qualname = sqlalchemy.engine

[logger_alembic]
level = INFO
handlers =
qualname = alembic

[handler_console]
class = StreamHandler
args = (sys.stderr,)
level = NOTSET
formatter = generic

[formatter_generic]
format = %(levelname)-5.5s [%(name)s] %(message)s
datefmt = %H:%M:%S
ALEMBIC_INI

cd /app

echo "Running Alembic migrations…"
alembic -c /tmp/alembic-rpc/alembic.ini upgrade head

# ---- 3. Seed data if table is empty ----
echo "Checking for seed data…"
if [ -f "/app/data/processed/movies_clean.csv" ]; then
    row_count=$(python -c "
import os, psycopg
conn = psycopg.connect(os.environ['DATABASE_URL'])
cur = conn.execute('SELECT COUNT(*) FROM movies')
print(cur.fetchone()[0])
conn.close()
")

    if [ "$row_count" -eq 0 ]; then
        echo "Database is empty — loading seed data…"
        python scripts/load_movies.py
        echo "Seed data loaded successfully."
    else
        echo "Database already contains $row_count movies — skipping seed load."
    fi
else
    echo "No seed data file found at /app/data/processed/movies_clean.csv — skipping."
fi

echo "Initializing – done."

# ---- 4. Execute CMD ----
exec "$@"

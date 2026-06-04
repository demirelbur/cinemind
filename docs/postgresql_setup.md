# PostgreSQL Setup (macOS)

> This guide is for local development on your own machine.
> Do not reuse these commands as-is for production.

If you already use Homebrew:

```bash
brew update
brew install postgresql@16
```

## Start PostgreSQL

```bash
brew services start postgresql@16
```

## Verify installation

```bash
psql --version
brew services list
# Should show: postgresql@16  started  ...
```

## Connect to PostgreSQL

```bash
psql postgres
```

You should see: `postgres=#`

## Create the database

```sql
CREATE DATABASE cinemind_db;
```

## Create a user

```sql
CREATE USER cinemind_user
  WITH LOGIN
  PASSWORD '<strong_password>'
  NOSUPERUSER
  NOCREATEDB
  NOCREATEROLE;

GRANT CONNECT ON DATABASE cinemind_db TO cinemind_user;
```

Connect to the new database:

```sql
\c cinemind_db
GRANT USAGE ON SCHEMA public TO cinemind_user;
GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA public TO cinemind_user;
GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA public TO cinemind_user;
```

Write permissions are intentional for the enrichment pipeline.

## Set DATABASE_URL in .env

```
DATABASE_URL=postgresql://cinemind_user:<strong_password>@localhost:5432/cinemind_db
```

## Production note

For production, additionally harden PostgreSQL with restricted network exposure, host-based authentication rules, TLS, credential rotation, and backup policy.

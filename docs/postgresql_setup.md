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
```

## Verify PostgreSQL is running

```bash
brew services list
```

You should see something like:

```bash
postgresql@16  started  ...
```

If it is not started:

```bash
brew services start postgresql@16
```

## Connect to PostgreSQL

```bash
psql postgres
```

If it works, you will see:

```bash
postgres=#
```

## Create the database

Inside `psql`, run:

```sql
CREATE DATABASE cinemind;
```

Then check:

```sql
\l
```

## Create a user

Still inside `psql`:

```sql
CREATE USER cinemind_user
  WITH LOGIN
  PASSWORD '<strong_password>'
  NOSUPERUSER
  NOCREATEDB
  NOCREATEROLE;

GRANT CONNECT ON DATABASE cinemind TO cinemind_user;
```

Then grant schema/table access inside the `cinemind` database:

```sql
\c cinemind
GRANT USAGE ON SCHEMA public TO cinemind_user;
GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA public TO cinemind_user;
GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA public TO cinemind_user;
```

Note: write permissions are intentional in this dev-first setup and support upcoming features such as semantic-search-related data workflows.

Use a strong password and store it in your local `.env` file only.
Do not commit secrets to Git.

Optional password generation example:

```bash
openssl rand -base64 24
```

## Test the connection

Exit:

```sql
\q
```

Then run:

```bash
psql -U cinemind_user -d cinemind
```

## Production note

For production, additionally harden PostgreSQL with restricted network exposure,
host-based authentication rules, TLS, credential rotation, and backup policy.

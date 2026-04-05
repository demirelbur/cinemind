# PostgreSQL Setup (macOS)

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
CREATE USER cinemind_user WITH PASSWORD 'password';
ALTER USER cinemind_user WITH SUPERUSER;
```

For local development, `SUPERUSER` is acceptable and simpler.

## Test the connection

Exit:

```sql
\q
```

Then run:

```bash
psql -U cinemind_user -d cinemind
```

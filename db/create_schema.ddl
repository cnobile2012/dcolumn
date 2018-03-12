/*
 * $ sudo -u postgres psql template1 -f db/create_schema.ddl
 */

DROP DATABASE IF EXISTS dcolumn;
CREATE DATABASE dcolumn;

DO
$body$
BEGIN
  IF NOT EXISTS (SELECT * FROM pg_catalog.pg_user WHERE pg_user.usename = 'dcolumn')
    THEN
      CREATE USER dcolumn WITH PASSWORD 'dcolumn';
      ALTER USER dcolumn CREATEDB;
  END IF;
END
$body$;

BEGIN;
  GRANT ALL PRIVILEGES ON DATABASE dcolumn TO dcolumn;
  ALTER ROLE dcolumn SET client_encoding TO 'utf8';
  ALTER ROLE dcolumn SET default_transaction_isolation TO 'read committed';
  ALTER ROLE dcolumn SET timezone TO 'UTC';
COMMIT;

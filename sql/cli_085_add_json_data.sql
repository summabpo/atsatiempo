-- =============================================================================
-- Campo json_data en cli_085_acciones_decisivas (Cli085AccionesDecisivas)
-- Equivale a la migración Django 0027_cli085accionesdecisivas_json_data
-- Ejecuta SOLO el bloque que corresponda a tu motor. No hace falta si ya
-- aplicaste: python manage.py migrate cliente
-- =============================================================================

-- -----------------------------------------------------------------------------
-- PostgreSQL (django.db.backends.postgresql)
-- JSONField de Django usa el tipo jsonb.
-- -----------------------------------------------------------------------------
ALTER TABLE cli_085_acciones_decisivas
    ADD COLUMN IF NOT EXISTS json_data jsonb NULL;

-- Si tu versión de PostgreSQL no soporta IF NOT EXISTS en ADD COLUMN:
-- ALTER TABLE cli_085_acciones_decisivas ADD COLUMN json_data jsonb NULL;


-- -----------------------------------------------------------------------------
-- MySQL / MariaDB 10.2+ (django.db.backends.mysql)
-- -----------------------------------------------------------------------------
-- ALTER TABLE cli_085_acciones_decisivas
--     ADD COLUMN json_data JSON NULL;


-- -----------------------------------------------------------------------------
-- Microsoft SQL Server (django.db.backends.mssql o similar)
-- -----------------------------------------------------------------------------
-- ALTER TABLE cli_085_acciones_decisivas
--     ADD json_data NVARCHAR(MAX) NULL;


-- -----------------------------------------------------------------------------
-- SQLite (django.db.backends.sqlite3)
-- -----------------------------------------------------------------------------
-- ALTER TABLE cli_085_acciones_decisivas
--     ADD COLUMN json_data TEXT NULL;

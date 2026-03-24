-- sql/create_tables.sql
-- ============================================================
-- Ireland Rent Tracker — Redshift Table Definitions
--
-- What is a schema?
-- A schema is the structure of your database.
-- It defines what tables exist and what columns they have.
-- You run this ONCE to set up the database.
-- ============================================================


-- ── Raw layer ──────────────────────────────────────────────
-- This table holds data exactly as it came from S3
-- No transformations — just raw data
-- In data engineering this is called the "raw" or "bronze" layer

CREATE SCHEMA IF NOT EXISTS raw;

CREATE TABLE IF NOT EXISTS raw.rtb_rents (
    year                INTEGER,
    bedrooms            VARCHAR(50),
    property_type       VARCHAR(100),
    location_code       VARCHAR(20),
    location            VARCHAR(200),
    avg_monthly_rent    DECIMAL(10, 2),
    county              VARCHAR(100),
    scraped_at          TIMESTAMP
);


-- ── Staging layer ──────────────────────────────────────────
-- Cleaned and standardised version of raw data
-- dbt will create the actual views/tables here
-- This is called the "silver" layer

CREATE SCHEMA IF NOT EXISTS staging;


-- ── Marts layer ────────────────────────────────────────────
-- Final tables ready for the dashboard
-- Aggregated, business-friendly
-- This is called the "gold" layer

CREATE SCHEMA IF NOT EXISTS marts;
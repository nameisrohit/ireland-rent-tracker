-- models/staging/stg_rents.sql
-- ============================================================
-- Staging model — cleans raw RTB rent data
--
-- What does this do?
-- 1. Selects only columns we need
-- 2. Standardises county names
-- 3. Filters out invalid rows
-- 4. Casts data types correctly
--
-- dbt handles CREATE TABLE automatically
-- We just write SELECT — that's the power of dbt
-- ============================================================

WITH source AS (
    -- Pull from raw source table
    -- {{ source('raw_data', 'rtb_rents') }} resolves to
    -- dev.raw_data.rtb_rents in Redshift
    SELECT * FROM {{ source('raw_data', 'rtb_rents') }}
),

cleaned AS (
    SELECT
        year::INTEGER                           AS year,
        TRIM(location)                          AS location,
        TRIM(bedrooms)                          AS bedrooms,
        TRIM(property_type)                     AS property_type,
        avg_monthly_rent::DECIMAL(10,2)         AS avg_monthly_rent,

        -- Standardise county names
        -- Some counties come as "Dublin 1", "Dublin 4" etc
        -- We keep those as-is for Dublin postal districts
        CASE
            WHEN county ILIKE '%dublin%'    THEN TRIM(county)
            WHEN county ILIKE '%cork%'      THEN 'Cork'
            WHEN county ILIKE '%galway%'    THEN 'Galway'
            WHEN county ILIKE '%limerick%'  THEN 'Limerick'
            WHEN county ILIKE '%waterford%' THEN 'Waterford'
            WHEN county ILIKE '%kildare%'   THEN 'Kildare'
            WHEN county ILIKE '%meath%'     THEN 'Meath'
            WHEN county ILIKE '%wicklow%'   THEN 'Wicklow'
            WHEN county ILIKE '%wexford%'   THEN 'Wexford'
            WHEN county ILIKE '%kilkenny%'  THEN 'Kilkenny'
            WHEN county ILIKE '%tipperary%' THEN 'Tipperary'
            WHEN county ILIKE '%clare%'     THEN 'Clare'
            WHEN county ILIKE '%kerry%'     THEN 'Kerry'
            WHEN county ILIKE '%mayo%'      THEN 'Mayo'
            WHEN county ILIKE '%sligo%'     THEN 'Sligo'
            WHEN county ILIKE '%donegal%'   THEN 'Donegal'
            WHEN county ILIKE '%louth%'     THEN 'Louth'
            WHEN county ILIKE '%cavan%'     THEN 'Cavan'
            WHEN county ILIKE '%monaghan%'  THEN 'Monaghan'
            WHEN county ILIKE '%roscommon%' THEN 'Roscommon'
            WHEN county ILIKE '%leitrim%'   THEN 'Leitrim'
            WHEN county ILIKE '%longford%'  THEN 'Longford'
            WHEN county ILIKE '%westmeath%' THEN 'Westmeath'
            WHEN county ILIKE '%offaly%'    THEN 'Offaly'
            WHEN county ILIKE '%laois%'     THEN 'Laois'
            WHEN county ILIKE '%carlow%'    THEN 'Carlow'
            ELSE TRIM(county)
        END                                     AS county

    FROM source

    -- Only keep rows with valid rent values
    WHERE avg_monthly_rent IS NOT NULL
    AND avg_monthly_rent > 0
    AND year BETWEEN 2008 AND 2024
)

SELECT * FROM cleaned
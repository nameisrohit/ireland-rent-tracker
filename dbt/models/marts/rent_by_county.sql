-- models/marts/rent_by_county.sql
-- Average rent per county per year
-- This feeds the county comparison chart in the dashboard

WITH base AS (
    SELECT * FROM {{ ref('stg_rents') }}
    WHERE bedrooms = 'All bedrooms'
    AND property_type = 'All property types'
),

aggregated AS (
    SELECT
        year,
        county,
        ROUND(AVG(avg_monthly_rent), 2)  AS avg_monthly_rent,
        COUNT(*)                          AS location_count
    FROM base
    GROUP BY year, county
),

with_yoy AS (
    SELECT
        year,
        county,
        avg_monthly_rent,
        location_count,
        -- LAG gets the previous year's rent for the same county
        -- This is how we calculate year-on-year change
        LAG(avg_monthly_rent) OVER (
            PARTITION BY county
            ORDER BY year
        ) AS prev_year_rent
    FROM aggregated
)

SELECT
    year,
    county,
    avg_monthly_rent,
    location_count,
    prev_year_rent,
    -- Calculate % change from previous year
    CASE
        WHEN prev_year_rent IS NOT NULL AND prev_year_rent > 0
        THEN ROUND(
            ((avg_monthly_rent - prev_year_rent) / prev_year_rent) * 100
        , 2)
        ELSE NULL
    END AS yoy_change_pct
FROM with_yoy
ORDER BY county, year
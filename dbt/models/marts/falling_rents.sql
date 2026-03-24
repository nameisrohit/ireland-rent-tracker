-- models/marts/falling_rents.sql
-- Areas where rent is falling year on year
-- This is one of the most interesting insights in the dashboard

WITH base AS (
    SELECT
        year,
        location,
        county,
        ROUND(AVG(avg_monthly_rent), 2) AS avg_monthly_rent
    FROM {{ ref('stg_rents') }}
    WHERE bedrooms = 'All bedrooms'
    AND property_type = 'All property types'
    GROUP BY year, location, county
),

with_prev AS (
    SELECT
        year,
        location,
        county,
        avg_monthly_rent,
        LAG(avg_monthly_rent) OVER (
            PARTITION BY location
            ORDER BY year
        ) AS prev_year_rent
    FROM base
)

SELECT
    year,
    location,
    county,
    avg_monthly_rent,
    prev_year_rent,
    ROUND(
        ((avg_monthly_rent - prev_year_rent) / prev_year_rent) * 100
    , 2) AS change_pct
FROM with_prev
WHERE prev_year_rent IS NOT NULL
AND avg_monthly_rent < prev_year_rent  -- Only falling rents
ORDER BY change_pct ASC               -- Biggest drops first
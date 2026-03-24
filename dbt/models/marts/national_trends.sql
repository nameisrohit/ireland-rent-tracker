-- models/marts/national_trends.sql
-- National average rent trends year by year
-- This feeds the main trend line chart

WITH yearly AS (
    SELECT
        year,
        ROUND(AVG(avg_monthly_rent), 2) AS avg_monthly_rent,
        ROUND(MIN(avg_monthly_rent), 2) AS min_rent,
        ROUND(MAX(avg_monthly_rent), 2) AS max_rent,
        COUNT(DISTINCT county)           AS counties_covered
    FROM {{ ref('stg_rents') }}
    WHERE bedrooms = 'All bedrooms'
    AND property_type = 'All property types'
    GROUP BY year
)

SELECT
    year,
    avg_monthly_rent,
    min_rent,
    max_rent,
    counties_covered,
    LAG(avg_monthly_rent) OVER (ORDER BY year) AS prev_year_rent,
    CASE
        WHEN LAG(avg_monthly_rent) OVER (ORDER BY year) IS NOT NULL
        THEN ROUND(
            ((avg_monthly_rent - LAG(avg_monthly_rent) OVER (ORDER BY year))
            / LAG(avg_monthly_rent) OVER (ORDER BY year)) * 100
        , 2)
        ELSE NULL
    END AS yoy_change_pct
FROM yearly
ORDER BY year
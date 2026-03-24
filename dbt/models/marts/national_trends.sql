-- models/marts/national_trends.sql
-- National average rent trends year by year

SELECT
    year,
    avg_monthly_rent,
    min_rent,
    max_rent,
    counties_covered,
    prev_year_rent,
    CASE
        WHEN prev_year_rent IS NOT NULL AND prev_year_rent > 0
        THEN ROUND(
            ((avg_monthly_rent - prev_year_rent) / prev_year_rent) * 100
        , 2)
        ELSE NULL
    END AS yoy_change_pct
FROM (
    SELECT
        year,
        ROUND(AVG(avg_monthly_rent), 2)  AS avg_monthly_rent,
        ROUND(MIN(avg_monthly_rent), 2)  AS min_rent,
        ROUND(MAX(avg_monthly_rent), 2)  AS max_rent,
        COUNT(DISTINCT county)            AS counties_covered,
        LAG(ROUND(AVG(avg_monthly_rent), 2)) OVER (ORDER BY year) AS prev_year_rent
    FROM {{ ref('stg_rents') }}
    WHERE bedrooms = 'All bedrooms'
    AND property_type = 'All property types'
    GROUP BY year
) yearly
ORDER BY year
-- models/marts/rent_by_bedrooms.sql
-- Average rent broken down by bedroom count
-- This feeds the bedroom comparison chart

SELECT
    year,
    county,
    bedrooms,
    ROUND(AVG(avg_monthly_rent), 2) AS avg_monthly_rent,
    COUNT(*)                         AS sample_size
FROM {{ ref('stg_rents') }}
WHERE bedrooms != 'All bedrooms'
AND property_type = 'All property types'
AND avg_monthly_rent > 0
GROUP BY year, county, bedrooms
ORDER BY year, county, bedrooms
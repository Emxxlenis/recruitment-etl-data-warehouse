SELECT 
    c.country_name,
    d.year,
    COUNT(*) AS total_hires,
    SUM(CASE WHEN f.data_quality_flag = 'Clean' THEN 1 ELSE 0 END) AS clean_hires,
    SUM(CASE WHEN COALESCE(f.data_quality_flag, '') <> 'Clean' THEN 1 ELSE 0 END) AS flagged_hires
FROM fact_applications f
JOIN dim_country c 
    ON f.country_id = c.country_id
JOIN dim_date d 
    ON f.date_id = d.date_id
WHERE f.is_hired = 1 
  AND c.country_name IN ('United States of America', 'Brazil', 'Colombia', 'Ecuador')
GROUP BY c.country_name, d.year
ORDER BY c.country_name, d.year;
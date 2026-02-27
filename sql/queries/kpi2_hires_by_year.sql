-- Cast year to text so Power BI treats it as a category (discrete axis, not continuous line)
SELECT 
    CAST(d.year AS TEXT) AS year,
    COUNT(*) AS total_hires,
    SUM(CASE WHEN f.data_quality_flag = 'Clean' THEN 1 ELSE 0 END) AS clean_hires,
    SUM(CASE WHEN COALESCE(f.data_quality_flag, '') <> 'Clean' THEN 1 ELSE 0 END) AS flagged_hires
FROM fact_applications f
JOIN dim_date d 
    ON f.date_id = d.date_id
WHERE f.is_hired = 1
GROUP BY d.year
ORDER BY d.year DESC;
SELECT 
    t.technology_name, 
    COUNT(*) AS total_hires,
    SUM(CASE WHEN f.data_quality_flag = 'Clean' THEN 1 ELSE 0 END) AS clean_hires,
    SUM(CASE WHEN COALESCE(f.data_quality_flag, '') <> 'Clean' THEN 1 ELSE 0 END) AS flagged_hires
FROM fact_applications f
JOIN dim_technology t 
    ON f.technology_id = t.technology_id
WHERE f.is_hired = 1
GROUP BY t.technology_name
ORDER BY total_hires DESC;
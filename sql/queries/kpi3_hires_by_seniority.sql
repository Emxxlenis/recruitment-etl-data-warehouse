SELECT 
    s.seniority_name, 
    COUNT(*) AS total_hires,
    SUM(CASE WHEN f.data_quality_flag = 'Clean' THEN 1 ELSE 0 END) AS clean_hires,
    SUM(CASE WHEN COALESCE(f.data_quality_flag, '') <> 'Clean' THEN 1 ELSE 0 END) AS flagged_hires
FROM fact_applications f
JOIN dim_seniority s 
    ON f.seniority_id = s.seniority_id
WHERE f.is_hired = 1
GROUP BY s.seniority_name
ORDER BY total_hires DESC;
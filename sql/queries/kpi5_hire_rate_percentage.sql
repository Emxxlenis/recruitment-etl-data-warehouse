SELECT 
    (SUM(is_hired) * 1.0 / COUNT(*)) * 100 AS hire_rate_percentage,
    (
        SUM(CASE WHEN is_hired = 1 AND data_quality_flag = 'Clean' THEN 1 ELSE 0 END) * 1.0
        / NULLIF(SUM(CASE WHEN data_quality_flag = 'Clean' THEN 1 ELSE 0 END), 0)
    ) * 100 AS hire_rate_clean_percentage,
    (
        SUM(CASE WHEN is_hired = 1 AND COALESCE(data_quality_flag, '') <> 'Clean' THEN 1 ELSE 0 END) * 1.0
        / NULLIF(SUM(CASE WHEN COALESCE(data_quality_flag, '') <> 'Clean' THEN 1 ELSE 0 END), 0)
    ) * 100 AS hire_rate_flagged_percentage
FROM fact_applications;
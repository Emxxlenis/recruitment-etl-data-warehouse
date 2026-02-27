SELECT 
    AVG(code_challenge_score) AS avg_code_score_all_hired,
    AVG(technical_interview_score) AS avg_interview_score_all_hired,
    AVG(CASE WHEN data_quality_flag = 'Clean' THEN code_challenge_score END) AS avg_code_score_clean_hired,
    AVG(CASE WHEN data_quality_flag = 'Clean' THEN technical_interview_score END) AS avg_interview_score_clean_hired,
    AVG(CASE WHEN COALESCE(data_quality_flag, '') <> 'Clean' THEN code_challenge_score END) AS avg_code_score_flagged_hired,
    AVG(CASE WHEN COALESCE(data_quality_flag, '') <> 'Clean' THEN technical_interview_score END) AS avg_interview_score_flagged_hired
FROM fact_applications
WHERE is_hired = 1;
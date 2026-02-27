-- Dimensions
CREATE TABLE IF NOT EXISTS dim_technology (
    technology_id SERIAL PRIMARY KEY, -- SERIAL enables auto-increment in PostgreSQL
    technology_name VARCHAR(255) NOT NULL
);

CREATE TABLE IF NOT EXISTS dim_seniority (
    seniority_id SERIAL PRIMARY KEY,
    seniority_name VARCHAR(50) NOT NULL
);

CREATE TABLE IF NOT EXISTS dim_country (
    country_id SERIAL PRIMARY KEY,
    country_name VARCHAR(100) NOT NULL
);

CREATE TABLE IF NOT EXISTS dim_candidate (
    candidate_id SERIAL PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL, -- UNIQUE added based on schema design
    first_name VARCHAR(100),
    last_name VARCHAR(100)
);

CREATE TABLE IF NOT EXISTS dim_date (
    date_id INTEGER PRIMARY KEY, -- No auto-increment (YYYYMMDD format)
    full_date DATE NOT NULL,
    year INTEGER,
    month INTEGER,
    quarter INTEGER
);

-- Fact Table
CREATE TABLE IF NOT EXISTS fact_applications (
    application_id SERIAL PRIMARY KEY,
    candidate_id INTEGER NOT NULL,
    date_id INTEGER NOT NULL,
    country_id INTEGER NOT NULL,
    technology_id INTEGER NOT NULL,
    seniority_id INTEGER NOT NULL,
    yoe INTEGER, -- Renamed from years_of_experience to match schema
    code_challenge_score INTEGER,
    technical_interview_score INTEGER,
    is_hired INTEGER CHECK (is_hired IN (0, 1)), -- Constraint to enforce 0 or 1
    data_quality_flag VARCHAR(255),
    
    FOREIGN KEY (candidate_id) REFERENCES dim_candidate(candidate_id),
    FOREIGN KEY (date_id) REFERENCES dim_date(date_id),
    FOREIGN KEY (country_id) REFERENCES dim_country(country_id),
    FOREIGN KEY (technology_id) REFERENCES dim_technology(technology_id),
    FOREIGN KEY (seniority_id) REFERENCES dim_seniority(seniority_id)
);
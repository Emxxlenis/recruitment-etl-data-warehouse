import pandas as pd

def generate_surrogate_keys(df, natural_key_col, surrogate_key_col):
    """
    Helper function to create dimensions.
    Extract unique values and assign incremental surrogate keys.
    """
    dim_df = pd.DataFrame(df[natural_key_col].unique(), columns=[natural_key_col])
    dim_df[surrogate_key_col] = range(1, len(dim_df) + 1)
    return dim_df

def data_quality_checks(row):
    """
    Build quality labels for the 'data_quality_flag' column.
    Detect logical anomalies without dropping records.
    """
    flags = []
    
    seniority = row['Seniority']
    yoe = row['YOE']

    # Seniority vs YOE consistency rules (without deleting rows)
    # These thresholds are quality-control rules to flag logical outliers.
    max_expected_yoe = {
        'Intern': 5,
        'Trainee': 8,
        'Junior': 15,
        'Mid-Level': 22,
    }
    min_expected_yoe = {
        'Senior': 2,
        'Lead': 5,
        'Architect': 8,
    }

    if seniority in max_expected_yoe and yoe > max_expected_yoe[seniority]:
        flags.append(f"Suspicious: {seniority} with >{max_expected_yoe[seniority]} YOE")

    if seniority in min_expected_yoe and yoe < min_expected_yoe[seniority]:
        flags.append(f"Suspicious: {seniority} with <{min_expected_yoe[seniority]} YOE")
        
    # Rule: scores outside expected range (0-10)
    if not (0 <= row['Code Challenge Score'] <= 10) or not (0 <= row['Technical Interview Score'] <= 10):
        flags.append("Invalid Score Range")
        
    return ", ".join(flags) if flags else "Clean"

def transform_data(df_raw):
    """
    Transform raw dataset into a dimensional model (Star Schema).
    Return a dictionary of DataFrames ready for SQL load.
    """
    print(f"   >>> Starting transform for {len(df_raw)} rows...")
    
    # Work on a copy to keep the in-memory raw dataset unchanged
    df = df_raw.copy()
    
    # ---------------------------------------------------------
    # 1. PRELIMINARY CLEANUP
    # ---------------------------------------------------------
    # Convert date column to datetime for downstream operations
    df['Application Date'] = pd.to_datetime(df['Application Date'])
    
    # ---------------------------------------------------------
    # 2. DIMENSION GENERATION (Context)
    # ---------------------------------------------------------
    
    # --- dim_technology ---
    dim_technology = generate_surrogate_keys(df, 'Technology', 'technology_id')
    dim_technology.rename(columns={'Technology': 'technology_name'}, inplace=True)
    
    # --- dim_seniority ---
    dim_seniority = generate_surrogate_keys(df, 'Seniority', 'seniority_id')
    dim_seniority.rename(columns={'Seniority': 'seniority_name'}, inplace=True)
    
    # --- dim_country ---
    dim_country = generate_surrogate_keys(df, 'Country', 'country_id')
    dim_country.rename(columns={'Country': 'country_name'}, inplace=True)
    
    # --- dim_date ---
    # Extract unique dates and derive calendar attributes
    unique_dates = pd.DataFrame(df['Application Date'].unique(), columns=['full_date'])
    unique_dates['date_id'] = unique_dates['full_date'].dt.strftime('%Y%m%d').astype(int)
    unique_dates['year'] = unique_dates['full_date'].dt.year
    unique_dates['month'] = unique_dates['full_date'].dt.month
    unique_dates['quarter'] = unique_dates['full_date'].dt.quarter
    
    dim_date = unique_dates[['date_id', 'full_date', 'year', 'month', 'quarter']]
    
    # --- dim_candidate (deduplication logic) ---
    # Sort by date so email dedup keeps the latest application
    df_sorted = df.sort_values(by='Application Date')
    
    # Keep First Name, Last Name, Email. Use Email as unique business key.
    dim_candidate = df_sorted[['First Name', 'Last Name', 'Email']].drop_duplicates(subset=['Email'], keep='last').copy()
    
    # Generate surrogate key
    dim_candidate['candidate_id'] = range(1, len(dim_candidate) + 1)
    
    # Rename columns to snake_case for SQL layer
    dim_candidate.rename(columns={
        'First Name': 'first_name', 
        'Last Name': 'last_name', 
        'Email': 'email'
    }, inplace=True)
    
    # Reorder columns
    dim_candidate = dim_candidate[['candidate_id', 'first_name', 'last_name', 'email']]

    # ---------------------------------------------------------
    # 3. FACT TABLE GENERATION (Metrics)
    # ---------------------------------------------------------
    
    # Merge source rows with dimensions to get surrogate IDs (foreign keys)
    # Use left joins to retain all source applications
    fact_df = df.merge(dim_technology, left_on='Technology', right_on='technology_name', how='left') \
                .merge(dim_seniority, left_on='Seniority', right_on='seniority_name', how='left') \
                .merge(dim_country, left_on='Country', right_on='country_name', how='left') \
                .merge(dim_candidate, left_on='Email', right_on='email', how='left')
    
    # For dim_date, convert application date to date_id (YYYYMMDD)
    fact_df['date_id_temp'] = fact_df['Application Date'].dt.strftime('%Y%m%d').astype(int)
    # We do not need an explicit dim_date merge because date_id is derived directly.
    # Referential consistency is guaranteed by construction.
    
    # --- Business rules ---
    
    # Rule: HIRED when both scores >= 7
    fact_df['is_hired'] = ((fact_df['Code Challenge Score'] >= 7) & 
                           (fact_df['Technical Interview Score'] >= 7)).astype(int)
    
    # Rule: data quality flag
    fact_df['data_quality_flag'] = fact_df.apply(data_quality_checks, axis=1)
    
    # Generate fact table primary key
    fact_df['application_id'] = range(1, len(fact_df) + 1)
    
    # Select and rename final columns to match SQL schema
    fact_applications = fact_df[[
        'application_id',
        'candidate_id',
        'date_id_temp',      # renamed to date_id below
        'country_id',
        'technology_id',
        'seniority_id',
        'YOE',               # renamed below
        'Code Challenge Score',
        'Technical Interview Score',
        'is_hired',
        'data_quality_flag'
    ]].copy()
    
    fact_applications.columns = [
        'application_id', 'candidate_id', 'date_id', 'country_id', 'technology_id', 'seniority_id',
        'yoe', 'code_challenge_score', 'technical_interview_score', 'is_hired', 'data_quality_flag'
    ]

    print(f"   >>> Transform completed. Fact table rows: {len(fact_applications)}.")

    # ---------------------------------------------------------
    # 4. OUTPUT
    # ---------------------------------------------------------
    # Return dictionary:
    # key   = exact SQL table name
    # value = transformed DataFrame
    
    return {
        "dim_technology": dim_technology,
        "dim_seniority": dim_seniority,
        "dim_country": dim_country,
        "dim_date": dim_date,
        "dim_candidate": dim_candidate,
        "fact_applications": fact_applications
    }
import pandas as pd
import os


REQUIRED_COLUMNS = [
    "First Name",
    "Last Name",
    "Email",
    "Country",
    "Application Date",
    "YOE",
    "Seniority",
    "Technology",
    "Code Challenge Score",
    "Technical Interview Score",
]


def _validate_data_types(df: pd.DataFrame) -> None:
    """
    Validate key columns have the expected data types.
    Raise a descriptive ValueError when validation fails.
    """
    # 1) Validate all required columns exist
    missing = [col for col in REQUIRED_COLUMNS if col not in df.columns]
    if missing:
        raise ValueError(f"Missing required CSV columns: {missing}")

    # 2) Validate Application Date can be parsed as date
    parsed_dates = pd.to_datetime(df["Application Date"], errors="coerce")
    invalid_dates = parsed_dates.isna().sum()
    if invalid_dates > 0:
        raise ValueError(
            f"Column 'Application Date' contains {invalid_dates} non-date values."
        )

    # 3) Validate YOE and score columns are numeric
    numeric_cols = ["YOE", "Code Challenge Score", "Technical Interview Score"]
    for col in numeric_cols:
        numeric_series = pd.to_numeric(df[col], errors="coerce")
        invalid_numerics = numeric_series.isna().sum()
        if invalid_numerics > 0:
            raise ValueError(
                f"Column '{col}' contains {invalid_numerics} non-numeric values."
            )


def extract_data(filepath):
    """
    Read the raw CSV file and return a DataFrame.
    Handle missing-file errors and validate basic data types.
    """
    print(f"Looking for file at: {filepath}")

    if not os.path.exists(filepath):
        raise FileNotFoundError(f"File {filepath} does not exist. Check the path.")

    try:
        # Try ';' first (common CSV separator in LATAM/Europe datasets)
        df = pd.read_csv(filepath, sep=";")

        # Quick fallback: if only one column was read, separator is likely ","
        if df.shape[1] == 1:
            df = pd.read_csv(filepath, sep=",")

        # Explicit data type validation (workshop requirement)
        _validate_data_types(df)

        print(f"Extract completed: {df.shape[0]} rows loaded.")
        return df
    except Exception as e:
        print(f"Extract error: {e}")
        raise
import os
import sqlite3

import pandas as pd


BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def get_db_path() -> str:
    """
    Return Data Warehouse path.
    Prefer etl_workshop.db in project root; if missing,
    fall back to a copy under sql/.
    """
    root_db = os.path.join(BASE_DIR, "etl_workshop.db")
    sql_db = os.path.join(BASE_DIR, "sql", "etl_workshop.db")

    if os.path.exists(root_db):
        return root_db
    if os.path.exists(sql_db):
        return sql_db

    raise FileNotFoundError(
        f"DW not found at either {root_db} or {sql_db}. "
        "Run the ETL pipeline first."
    )


def load_sql(query_name: str) -> str:
    queries_dir = os.path.join(BASE_DIR, "sql", "queries")
    filename = f"{query_name}.sql"
    path = os.path.join(queries_dir, filename)
    if not os.path.exists(path):
        raise FileNotFoundError(f"SQL file not found: {path}")
    with open(path, "r", encoding="utf-8") as f:
        return f.read()


def run_query(conn: sqlite3.Connection, sql: str) -> pd.DataFrame:
    return pd.read_sql(sql, conn)


def main():
    db_path = get_db_path()
    print(f"Usando Data Warehouse: {db_path}")

    conn = sqlite3.connect(db_path)

    kpi_files = {
        "kpi1_hires_by_technology": "Hires by Technology",
        "kpi2_hires_by_year": "Hires by Year",
        "kpi3_hires_by_seniority": "Hires by Seniority",
        "kpi4_hires_by_country": "Hires by Country over Years",
        "kpi5_hire_rate_percentage": "Hire Rate (%)",
        "kpi6_hired_quality_scores": "Average Scores (Hired)",
    }

    try:
        # Reference metric: total hires from fact table
        total_hires_overall = pd.read_sql(
            "SELECT SUM(is_hired) AS total_hires FROM fact_applications", conn
        )["total_hires"].iloc[0]
        print(f"Total hires (fact_applications): {total_hires_overall}")

        print("\n=== KPI results ===")
        for file_key, title in kpi_files.items():
            print(f"\n--- {title} ({file_key}) ---")
            sql = load_sql(file_key)
            df = run_query(conn, sql)
            print(df.head())
            print(f"Rows returned: {len(df)}")

            # Lightweight KPI validations
            if file_key in {
                "kpi1_hires_by_technology",
                "kpi2_hires_by_year",
                "kpi3_hires_by_seniority",
            }:
                # total_hires sum should match global total_hires_overall
                kpi_sum = df["total_hires"].sum()
                print(f"KPI total_hires sum: {kpi_sum}")
                if kpi_sum != total_hires_overall:
                    print(
                        "WARNING: total_hires sum for this KPI "
                        "does not match global total hires."
                    )

            if file_key == "kpi5_hire_rate_percentage":
                val = df["hire_rate_percentage"].iloc[0]
                print(f"Hire rate (%): {val}")
                if not (0 <= val <= 100):
                    print("WARNING: hire rate is out of 0-100 range.")

            if file_key == "kpi6_hired_quality_scores":
                # Compatibility with both previous and current KPI6 schemas
                code_col = (
                    "avg_code_score_all_hired"
                    if "avg_code_score_all_hired" in df.columns
                    else "avg_code_score"
                )
                interview_col = (
                    "avg_interview_score_all_hired"
                    if "avg_interview_score_all_hired" in df.columns
                    else "avg_interview_score"
                )

                avg_code = df[code_col].iloc[0]
                avg_interview = df[interview_col].iloc[0]
                print(
                    f"Averages - Code Challenge: {avg_code}, "
                    f"Technical Interview: {avg_interview}"
                )
                for name, v in [
                    (code_col, avg_code),
                    (interview_col, avg_interview),
                ]:
                    if not (0 <= v <= 10):
                        print(f"WARNING: {name} is out of 0-10 range.")

    finally:
        conn.close()


if __name__ == "__main__":
    main()


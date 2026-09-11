import os
import sys
import time
import pandas as pd

# Add backend directory to sys.path so modules can be imported directly
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
BACKEND_DIR = os.path.abspath(os.path.join(CURRENT_DIR, ".."))
if BACKEND_DIR not in sys.path:
    sys.path.insert(0, BACKEND_DIR)

from database import engine, SessionLocal, init_db
from models import CrimeRecord


def seed_database(csv_path: str = None, batch_size: int = 5000):
    """
    Reads the historical Delhi crime CSV dataset and loads all records into the SQLite database.
    """
    if csv_path is None:
        candidate_1 = os.path.join(BACKEND_DIR, "data", "delhi_crime_2015_2025.csv")
        candidate_2 = os.path.join(BACKEND_DIR, "..", "data", "delhi_crime_2015_2025.csv")
        if os.path.exists(candidate_1):
            csv_path = candidate_1
        elif os.path.exists(candidate_2):
            csv_path = candidate_2
        else:
            print(f"[ERROR] Crime dataset not found in '{candidate_1}' or '{candidate_2}'.")
            return

    print("[*] Initializing database tables...")
    init_db()

    print(f"[*] Loading historical crime records from: {csv_path}")
    start_time = time.time()

    df = pd.read_csv(csv_path)
    total_raw_rows = len(df)
    print(f"[*] Parsed {total_raw_rows} raw crime records from CSV.")

    # 1. Deduplicate by crime_id within the CSV
    initial_count = len(df)
    df = df.drop_duplicates(subset=["crime_id"], keep="first")
    csv_duplicates = initial_count - len(df)

    # 2. Validate latitude & longitude bounds for National Capital Region (Delhi)
    # Latitude: ~28.0 to 29.5, Longitude: ~76.5 to 78.0
    valid_coords = (
        df["latitude"].notnull() &
        df["longitude"].notnull() &
        (df["latitude"] >= 28.0) & (df["latitude"] <= 29.5) &
        (df["longitude"] >= 76.5) & (df["longitude"] <= 78.0)
    )

    # 3. Validate mandatory fields
    valid_required = (
        df["crime_id"].notnull() &
        df["timestamp"].notnull() &
        df["date"].notnull() &
        df["year"].notnull() &
        df["crime_type"].notnull() &
        df["district"].notnull()
    )

    valid_mask = valid_coords & valid_required
    invalid_records = int((~valid_mask).sum())
    valid_df = df[valid_mask].copy()

    # 4. Check for existing records in SQLite to prevent duplicate PK constraint violations
    db = SessionLocal()
    existing_records = set()
    try:
        existing_ids = db.query(CrimeRecord.crime_id).all()
        existing_records = {row[0] for row in existing_ids}
    except Exception:
        pass

    if existing_records:
        pre_filter = len(valid_df)
        valid_df = valid_df[~valid_df["crime_id"].isin(existing_records)]
        db_duplicates = pre_filter - len(valid_df)
    else:
        db_duplicates = 0

    total_rejected = csv_duplicates + invalid_records + db_duplicates

    # 5. Insert valid records into SQLite
    records_to_insert = len(valid_df)
    if records_to_insert > 0:
        print(f"[*] Inserting {records_to_insert} valid records into 'crime_records'...")
        valid_df = valid_df.where(pd.notnull(valid_df), None)
        valid_df.to_sql("crime_records", con=engine, if_exists="append", index=False, chunksize=batch_size)
    else:
        print("[*] No new records to insert.")

    elapsed = round(time.time() - start_time, 2)
    final_count = db.query(CrimeRecord).count()
    db.close()

    print("\n" + "=" * 50)
    print("DATABASE SEEDING SUMMARY")
    print("=" * 50)
    print(f"Total raw records in CSV:      {total_raw_rows}")
    print(f"Internal CSV duplicates:       {csv_duplicates}")
    print(f"Invalid / out-of-bounds rows:  {invalid_records}")
    print(f"Existing DB duplicates:        {db_duplicates}")
    print(f"Total rejected / skipped:      {total_rejected}")
    print(f"New records inserted:          {records_to_insert}")
    print(f"Total records now in database: {final_count}")
    print(f"Time elapsed:                  {elapsed}s")
    print("=" * 50 + "\n")

    return {
        "total_raw": total_raw_rows,
        "inserted": records_to_insert,
        "rejected": total_rejected,
        "final_count": final_count
    }


if __name__ == "__main__":
    csv_file = sys.argv[1] if len(sys.argv) > 1 else None
    seed_database(csv_file)


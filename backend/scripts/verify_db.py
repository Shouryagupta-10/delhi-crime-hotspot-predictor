import os
import sqlite3

db_path = os.path.join(os.path.dirname(__file__), "..", "rakshak.db")
db_path = os.path.abspath(db_path)

print(f"Database Path: {db_path}")
print(f"Database Exists: {os.path.exists(db_path)}")
print(f"Database File Size: {os.path.getsize(db_path):,} bytes")

conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# 1. Tables
cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
tables = [row[0] for row in cursor.fetchall()]
print(f"Tables Found: {tables}")

# 2. Schema
cursor.execute("PRAGMA table_info(crime_records);")
cols = cursor.fetchall()
print("\nTable Columns in 'crime_records':")
for c in cols:
    cid, name, col_type, notnull, dflt_val, pk = c
    print(f" - {name} ({col_type}) | PK: {bool(pk)} | NotNull: {bool(notnull)}")

# 3. Total Record Count
cursor.execute("SELECT COUNT(*) FROM crime_records;")
total_count = cursor.fetchone()[0]
print(f"\nTotal Records Inserted: {total_count:,}")

# 4. Lat/Lon Validity
cursor.execute("SELECT MIN(latitude), MAX(latitude), MIN(longitude), MAX(longitude) FROM crime_records;")
lat_min, lat_max, lon_min, lon_max = cursor.fetchone()
print(f"Latitude Range:  {lat_min} to {lat_max} (Valid for Delhi ~28.0 - 29.5)")
print(f"Longitude Range: {lon_min} to {lon_max} (Valid for Delhi ~76.5 - 78.0)")

# 5. Temporal Fields Validity
cursor.execute("SELECT MIN(year), MAX(year), MIN(month), MAX(month), MIN(hour), MAX(hour) FROM crime_records;")
y_min, y_max, m_min, m_max, h_min, h_max = cursor.fetchone()
print(f"Year Range:      {y_min} to {y_max}")
print(f"Month Range:     {m_min} to {m_max}")
print(f"Hour Range:      {h_min} to {h_max}")

cursor.execute("SELECT DISTINCT day_of_week FROM crime_records ORDER BY day_of_week;")
days = [row[0] for row in cursor.fetchall()]
print(f"Days of Week:    {days}")

# 6. Sample Records
cursor.execute("SELECT crime_id, timestamp, date, time, crime_type, district, latitude, longitude FROM crime_records LIMIT 3;")
print("\nSample Stored Records:")
for row in cursor.fetchall():
    print(f"  ID: {row[0]} | Time: {row[1]} | Type: {row[4]} | District: {row[5]} | Lat/Lon: ({row[6]}, {row[7]})")

# 7. Check for NULLs in essential fields
cursor.execute("""
    SELECT 
        SUM(CASE WHEN crime_id IS NULL THEN 1 ELSE 0 END),
        SUM(CASE WHEN latitude IS NULL THEN 1 ELSE 0 END),
        SUM(CASE WHEN longitude IS NULL THEN 1 ELSE 0 END),
        SUM(CASE WHEN year IS NULL THEN 1 ELSE 0 END),
        SUM(CASE WHEN crime_type IS NULL THEN 1 ELSE 0 END)
    FROM crime_records;
""")
null_counts = cursor.fetchone()
print(f"\nNull Check (crime_id, lat, lon, year, crime_type): {null_counts}")

conn.close()

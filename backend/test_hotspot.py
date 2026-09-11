import os
import sys

BACKEND_DIR = os.path.dirname(os.path.abspath(__file__))
if BACKEND_DIR not in sys.path:
    sys.path.insert(0, BACKEND_DIR)

from database import SessionLocal
from services.hotspot import detect_crime_hotspots

db = SessionLocal()
print("[*] Running DBSCAN Hotspot Detection on crime_records...")
results = detect_crime_hotspots(db, eps_km=0.5, min_samples=25)
db.close()

print(f"Total points analyzed:    {results['total_points_analyzed']:,}")
print(f"Total clusters detected:  {results['total_clusters_detected']}")
print(f"Clustered points:         {results['clustered_points_count']:,}")
print(f"Noise points:             {results['noise_points_count']:,} ({results['noise_percentage']}%)")
print(f"Execution time:           {results['execution_time_seconds']}s")

print("\nTop 5 Hotspot Clusters:")
for h in results['hotspots'][:5]:
    print(f" - Cluster {h['cluster_id']}: {h['crime_count']} crimes ({h['percentage_of_clustered_crimes']}% of clustered), Center: ({h['center_latitude']}, {h['center_longitude']}), District: {h['primary_district']}")

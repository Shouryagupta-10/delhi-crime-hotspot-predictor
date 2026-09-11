import urllib.request
import json

base_url = "http://127.0.0.1:8001"

def fetch_json(url_path):
    url = f"{base_url}{url_path}"
    req = urllib.request.Request(url)
    with urllib.request.urlopen(req) as resp:
        status = resp.status
        data = json.loads(resp.read().decode("utf-8"))
        return status, data

print("=" * 60)
print("TEST 1: GET /api/crimes/temporal/summary")
print("=" * 60)
status_summary, data_summary = fetch_json("/api/crimes/temporal/summary")
print(f"HTTP Status: {status_summary}")
print(json.dumps(data_summary, indent=2))

print("\n" + "=" * 60)
print("TEST 2: GET /api/crimes/temporal")
print("=" * 60)
status_full, data_full = fetch_json("/api/crimes/temporal")
print(f"HTTP Status: {status_full}")
print(f"Total Crimes Analyzed: {data_full['total_crimes_analyzed']}")
print(f"Hourly items count:    {len(data_full['hourly_distribution'])}")
print(f"Daily items count:     {len(data_full['day_of_week_distribution'])}")
print(f"Monthly items count:   {len(data_full['monthly_distribution'])}")
print(f"Yearly items count:    {len(data_full['yearly_distribution'])}")
print(f"Crime types count:     {len(data_full['crime_type_distribution'])}")
print(f"Districts count:       {len(data_full['district_distribution'])}")

print("\nSample Hourly (first 3):")
print(json.dumps(data_full['hourly_distribution'][:3], indent=2))

print("\nSample Daily (all 7):")
print(json.dumps(data_full['day_of_week_distribution'], indent=2))

print("\nSample Monthly (first 3):")
print(json.dumps(data_full['monthly_distribution'][:3], indent=2))

print("\n" + "=" * 60)
print("TEST 3: Filtered GET /api/crimes/temporal/summary?district=Central&crime_type=Robbery")
print("=" * 60)
status_filtered, data_filtered = fetch_json("/api/crimes/temporal/summary?district=Central&crime_type=Robbery")
print(f"HTTP Status: {status_filtered}")
print(json.dumps(data_filtered, indent=2))

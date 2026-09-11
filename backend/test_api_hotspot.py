import urllib.request
import json

base_url = "http://127.0.0.1:8001"

def call_api(endpoint):
    url = f"{base_url}{endpoint}"
    req = urllib.request.Request(url)
    with urllib.request.urlopen(req) as resp:
        status = resp.status
        data = json.loads(resp.read().decode("utf-8"))
        return status, data

print("[*] Calling GET /api/hotspots (default: eps=0.5km, min_samples=25)...")
status, data = call_api("/api/hotspots")
print(f"HTTP Status: {status}")
print(f"Algorithm:   {data['algorithm']}")
print(f"Explanation: {data['distance_metric_explanation']}")
print(f"Parameters:  {data['parameters']}")
print(f"Total Points: {data['total_points_analyzed']}")
print(f"Clusters Detected: {data['total_clusters_detected']}")
print(f"Clustered Points:  {data['clustered_points_count']}")
print(f"Noise Points:      {data['noise_points_count']} ({data['noise_percentage']}%)")
print(f"Execution Time:    {data['execution_time_seconds']}s")

print("\n[*] Sample Top Hotspot:")
print(json.dumps(data['hotspots'][0], indent=2))

print("\n[*] Testing with query parameters: /api/hotspots?district=Central&eps_km=0.4&min_samples=20")
status2, data2 = call_api("/api/hotspots?district=Central&eps_km=0.4&min_samples=20")
print(f"HTTP Status: {status2}")
print(f"Central Delhi Points:    {data2['total_points_analyzed']}")
print(f"Central Clusters Found:  {data2['total_clusters_detected']}")
print(f"Central Clustered:       {data2['clustered_points_count']}")
print(f"Central Noise:           {data2['noise_points_count']} ({data2['noise_percentage']}%)")

# Save sample output for reporting
with open("sample_hotspot_response.json", "w") as f:
    # Save trimmed version of data with first 3 hotspots
    trimmed = dict(data)
    trimmed["hotspots"] = trimmed["hotspots"][:3]
    json.dump(trimmed, f, indent=2)

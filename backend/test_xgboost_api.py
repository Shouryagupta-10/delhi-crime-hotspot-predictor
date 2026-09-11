import urllib.request
import json
import time

base_url = "http://127.0.0.1:8001"

def http_get(endpoint):
    url = f"{base_url}{endpoint}"
    req = urllib.request.Request(url)
    with urllib.request.urlopen(req) as resp:
        return resp.status, json.loads(resp.read().decode("utf-8"))

def http_post(endpoint, payload):
    url = f"{base_url}{endpoint}"
    data_bytes = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(url, data=data_bytes, headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req) as resp:
        return resp.status, json.loads(resp.read().decode("utf-8"))

print("=" * 70)
print("TEST 1: GET /api/model/info")
print("=" * 70)
status, model_info = http_get("/api/model/info")
print(f"HTTP Status: {status}")
print(json.dumps(model_info, indent=2))

print("\n" + "=" * 70)
print("TEST 2: POST /api/predict-risk (Scenario 1: Late Night Central Delhi Robbery)")
print("=" * 70)
payload1 = {
    "latitude": 28.6432,
    "longitude": 77.2140,
    "hour": 23,
    "day": "Friday",
    "month": 8,
    "year": 2025,
    "district": "Central",
    "crime_type": "Robbery"
}
t0 = time.time()
status1, resp1 = http_post("/api/predict-risk", payload1)
lat1 = round((time.time() - t0) * 1000, 2)
print(f"HTTP Status: {status1} (Latency: {lat1}ms)")
print(json.dumps(resp1, indent=2))

print("\n" + "=" * 70)
print("TEST 3: POST /api/predict-risk (Scenario 2: Daytime Residential South Delhi)")
print("=" * 70)
payload2 = {
    "latitude": 28.5600,
    "longitude": 77.1900,
    "hour": 10,
    "day": "Monday",
    "month": 3,
    "year": 2024,
    "district": "South",
    "crime_type": "Pickpocketing / Theft"
}
t0 = time.time()
status2, resp2 = http_post("/api/predict-risk", payload2)
lat2 = round((time.time() - t0) * 1000, 2)
print(f"HTTP Status: {status2} (Latency: {lat2}ms)")
print(json.dumps(resp2, indent=2))

print("\n" + "=" * 70)
print("TEST 4: POST /api/predict-risk (Scenario 3: Omitted crime_type - General Area Risk)")
print("=" * 70)
payload3 = {
    "latitude": 28.6315,
    "longitude": 77.2167,
    "hour": 21,
    "day": "Saturday",
    "month": 10,
    "year": 2025,
    "district": "New Delhi"
}
t0 = time.time()
status3, resp3 = http_post("/api/predict-risk", payload3)
lat3 = round((time.time() - t0) * 1000, 2)
print(f"HTTP Status: {status3} (Latency: {lat3}ms)")
print(json.dumps(resp3, indent=2))

print("\n" + "=" * 70)
print("TEST 5: Regression Check on Existing Endpoints")
print("=" * 70)

endpoints = [
    ("/health", "Health Check"),
    ("/api/crimes/stats/summary", "Crime Statistics Summary"),
    ("/api/hotspots?eps_km=0.5&min_samples=25", "DBSCAN Hotspots"),
    ("/api/crimes/temporal", "Full Temporal Analysis"),
    ("/api/crimes/temporal/summary", "Temporal Summary"),
]

all_passed = True
for ep, name in endpoints:
    st, data = http_get(ep)
    passed = (st == 200)
    if not passed:
        all_passed = False
    print(f"[{'PASS' if passed else 'FAIL'}] {name} ({ep}) -> HTTP {st}")

print("\nAll endpoints operational:", all_passed)

"""
Unit tests for Rakshak.ai Emergency SOS Alert Dispatcher & Geofence Proximity
Validates:
- Real-time Haversine proximity calculations (<=100m geofence trigger)
- Warning state transitions when user is within 100m of a Red Danger Hotspot
- Distress payload formatting with Google Maps live telemetry link
- Recipient identification and primary designation
- High-priority FCM push notification parameters and safety beep audio tags
- Emergency SMS Gateway dispatch (Twilio, Fast2SMS, Webhooks, and simulation fallback)
"""

import os
import sys
import unittest

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from models.sos_dispatcher import (
    calculate_haversine_distance_meters,
    find_nearest_danger_hotspot,
    EmergencySOSDispatcher,
    DELHI_HOTSPOT_CENTROIDS
)


class TestEmergencySOSAlert(unittest.TestCase):
    def setUp(self):
        self.dispatcher = EmergencySOSDispatcher()
        # Rajiv Chowk hotspot centroid: 28.6328, 77.2197
        self.ref_spot = DELHI_HOTSPOT_CENTROIDS[0]

    def test_01_haversine_distance_accuracy(self):
        """Verifies Haversine distance matches physical ground truth in meters."""
        lat1, lon1 = 28.6328, 77.2197
        # Move approximately 50 meters north (1 deg lat ~= 111,000m -> 50m ~= 0.00045 deg)
        lat2, lon2 = lat1 + 0.00045, lon1
        dist = calculate_haversine_distance_meters(lat1, lon1, lat2, lon2)
        self.assertTrue(45.0 <= dist <= 55.0, f"Distance {dist} should be approx 50m")

    def test_02_danger_zone_geofence_under_100m(self):
        """Validates that locations <= 100m correctly trigger is_within_100m_danger_zone."""
        # Point within ~60m of Rajiv Chowk
        close_lat = self.ref_spot["lat"] + 0.00054
        close_lon = self.ref_spot["lon"]
        is_triggered, dist_m, spot = self.dispatcher.is_within_100m_danger_zone(close_lat, close_lon)

        self.assertTrue(is_triggered, "Should trigger geofence when <= 100m")
        self.assertLessEqual(dist_m, 100.0)
        self.assertEqual(spot["name"], self.ref_spot["name"])

    def test_03_danger_zone_geofence_safe_buffer(self):
        """Validates that points beyond 100m do not trigger emergency geofence."""
        # Chanakyapuri Safe Zone: ~4 km away from Rajiv Chowk
        safe_lat = 28.5983
        safe_lon = 77.1912
        is_triggered, dist_m, spot = self.dispatcher.is_within_100m_danger_zone(safe_lat, safe_lon)

        self.assertFalse(is_triggered, "Should not trigger geofence when beyond 100m")
        self.assertGreater(dist_m, 1000.0)

    def test_04_sos_payload_structure(self):
        """Verifies emergency distress payload adheres to all required specification fields."""
        lat, lon = 28.6328, 77.2197
        recipient_name = "Chief Sentinel Officer"
        recipient_phone = "+91 98719 01120"

        payload = self.dispatcher.build_sos_payload(
            lat=lat,
            lon=lon,
            recipient_name=recipient_name,
            recipient_phone=recipient_phone,
            hotspot_name=self.ref_spot["name"],
            distance_meters=42.5
        )

        # Check required fields
        self.assertIn("alert_id", payload)
        self.assertIn("timestamp", payload)
        self.assertEqual(payload["recipient"]["name"], recipient_name)
        self.assertEqual(payload["recipient"]["phone"], recipient_phone)
        self.assertTrue(payload["recipient"]["is_primary"])

        # Check live Google Maps link
        expected_maps_link = f"https://maps.google.com/?q={lat:.5f},{lon:.5f}"
        self.assertEqual(payload["location"]["google_maps_live_link"], expected_maps_link)
        self.assertIn(expected_maps_link, payload["message"])

        # Check distress message contents
        self.assertIn("EMERGENCY: User is in an active danger zone", payload["message"])
        self.assertIn("Immediate assistance requested", payload["message"])

        # Check high priority push notification parameters
        push = payload["push_notification"]
        self.assertEqual(push["priority"], "high")
        self.assertEqual(push["sound"], "safety_beep.mp3")
        self.assertEqual(push["channel_id"], "emergency_sos_high_priority")
        self.assertEqual(push["data"]["audio_tone"], "880Hz_alternating_pulse")

    def test_05_alert_dispatch_execution(self):
        """Verifies alert dispatch returns successful receipt and audit trace."""
        lat, lon = 28.6328, 77.2197
        payload = self.dispatcher.build_sos_payload(
            lat=lat,
            lon=lon,
            recipient_name="Parent Guardian",
            recipient_phone="+91 98100 12345",
            hotspot_name=self.ref_spot["name"],
            distance_meters=55.0
        )

        result = self.dispatcher.dispatch_alert(payload)

        self.assertTrue(result["success"])
        self.assertEqual(result["recipient_phone"], "+91 98100 12345")
        self.assertIn("https://maps.google.com", result["maps_live_link"])
        self.assertTrue(len(result["dispatched_channels"]) > 0)
        self.assertEqual(result["delivery_status"], "DELIVERED_TO_EMERGENCY_NETWORK")


if __name__ == "__main__":
    unittest.main()

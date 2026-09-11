"""
Automated Test Suite for Delhi Crime Hotspot & Premises Risk Predictor
Validates data integrity, Haversine DBSCAN clustering, supervised risk forecasting, and metrics.
"""

import os
import sys
import unittest
import numpy as np
import pandas as pd

# Add project root to sys.path
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from data.generate_delhi_data import generate_delhi_crime_dataset, DISTRICTS
from data.cleaner import clean_crime_dataset, CrimeDataCleaner
from models.cluster_engine import HotspotClusterEngine, compare_dbscan_vs_kmeans
from models.risk_predictor import DelhiCrimeRiskPredictor

class TestDelhiCrimePipeline(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.test_csv = os.path.join(PROJECT_ROOT, "data", "test_delhi_crime.csv")
        cls.test_raw_csv = os.path.join(PROJECT_ROOT, "data", "test_raw_delhi_crime.csv")
        cls.df = generate_delhi_crime_dataset(num_records=1500, output_path=cls.test_csv, raw_output_path=cls.test_raw_csv)

    @classmethod
    def tearDownClass(cls):
        for p in [cls.test_csv, cls.test_raw_csv]:
            if os.path.exists(p):
                os.remove(p)

    def test_01_dataset_integrity(self):
        """Validates that cleaned dataset contains confirmed reports, 15 districts, valid coordinates, and 0 nulls."""
        self.assertGreater(len(self.df), 800)
        self.assertGreaterEqual(self.df["district"].nunique(), 14)
        self.assertEqual(self.df["premises_type"].nunique(), 8)
        
        # Verify all records are confirmed police reports
        if "confirmation_status" in self.df.columns:
            self.assertTrue((self.df["confirmation_status"] == "Confirmed").all(), "Clean dataset must only contain Confirmed reports")
        
        # Verify latitude and longitude within National Capital Territory of Delhi
        self.assertTrue((self.df["latitude"] >= 28.30).all() and (self.df["latitude"] <= 28.95).all())
        self.assertTrue((self.df["longitude"] >= 76.80).all() and (self.df["longitude"] <= 77.50).all())
        
        # Verify 100% completeness: zero nulls across all critical columns
        critical_cols = ["record_id", "district", "premises_type", "crime_category", "hour", "latitude", "longitude", "risk_level"]
        for col in critical_cols:
            self.assertEqual(self.df[col].isnull().sum(), 0, f"Column {col} has null values")

    def test_02_haversine_dbscan_clustering(self):
        """Verifies DBSCAN clustering discovers dense clusters and separates noise using Haversine distance."""
        engine = HotspotClusterEngine(eps_meters=600.0, min_samples=10)
        engine.fit(self.df)
        
        self.assertTrue(engine.fitted)
        self.assertGreater(engine.num_clusters_, 5, "Should discover at least 5 dense hotspots in Delhi")
        self.assertGreaterEqual(engine.noise_ratio_, 0.0, "Noise ratio must be non-negative")
        self.assertIsNotNone(engine.hotspots_df)
        self.assertFalse(engine.hotspots_df.empty)
        
        # Test distance calculation
        dist = engine.get_distance_to_nearest_hotspot_km(28.6328, 77.2195)  # Connaught Place coordinates
        self.assertGreaterEqual(dist, 0.0)
        self.assertLess(dist, 50.0, "Distance within Delhi territory should be under 50 km")

    def test_03_supervised_risk_predictor(self):
        """Validates training pipeline, strict train/test split, and prediction API."""
        predictor = DelhiCrimeRiskPredictor(use_xgboost=True)
        metrics = predictor.train_and_evaluate(self.test_csv)
        
        # Verify metrics satisfy performance standards
        self.assertGreater(metrics["accuracy"], 0.75, "Model accuracy should exceed 75%")
        self.assertGreater(metrics["roc_auc"], 0.80, "Model ROC-AUC should exceed 0.80")
        self.assertGreater(metrics["f1_score"], 0.65, "Model F1 should exceed 0.65")
        
        # Verify real-time prediction output
        pred = predictor.predict_risk(
            district="New Delhi",
            premises_type="Transit & Metro Hub",
            hour=22,
            day_of_week="Friday",
            lat=28.6328,
            lon=77.2195
        )
        self.assertIn("high_risk_probability", pred)
        self.assertIn("risk_level", pred)
        self.assertIn("advisory", pred)
        self.assertTrue(0.0 <= pred["high_risk_probability"] <= 100.0)

    def test_04_dbscan_vs_kmeans_comparison(self):
        """Validates the algorithmic defense engine and comparison data."""
        _, defense = compare_dbscan_vs_kmeans(self.df, k_range=range(3, 7))
        self.assertIn("dbscan_summary", defense)
        self.assertIn("best_kmeans_summary", defense)
        self.assertIn("talking_points", defense)
        self.assertEqual(len(defense["talking_points"]), 4)

    def test_05_data_cleaning_filters_unconfirmed(self):
        """Validates that unconfirmed, pending, and dismissed reports are systematically excluded."""
        raw_mock = pd.DataFrame([
            {"record_id": "T-1", "confirmation_status": "Confirmed", "district": "New Delhi", "police_station": "Connaught Place", "crime_category": "Snatching (Chain/Mobile)", "premises_type": "Commercial & Retail Market", "date": "2025-05-01", "hour": 14, "minute": 20, "latitude": 28.6328, "longitude": 77.2195},
            {"record_id": "T-2", "confirmation_status": "Pending Investigation", "district": "Central", "police_station": "Karol Bagh", "crime_category": "Burglary & House Breaking", "premises_type": "Residential Gated Colony", "date": "2025-05-02", "hour": 2, "minute": 15, "latitude": 28.6517, "longitude": 77.1906},
            {"record_id": "T-3", "confirmation_status": "Unconfirmed / Unverified Tip", "district": "North", "police_station": "Civil Lines", "crime_category": "Motor Vehicle Theft", "premises_type": "Transit & Metro Hub", "date": "2025-05-03", "hour": 23, "minute": 45, "latitude": 28.6675, "longitude": 77.2285},
            {"record_id": "T-4", "confirmation_status": "False Alarm / Dismissed", "district": "South", "police_station": "Saket", "crime_category": "Assault & Public Brawl", "premises_type": "Parks & Isolated Environs", "date": "2025-05-04", "hour": 20, "minute": 10, "latitude": 28.5285, "longitude": 77.2185},
        ])
        clean_df, audit = clean_crime_dataset(raw_mock)
        self.assertEqual(len(clean_df), 1)
        self.assertEqual(clean_df.iloc[0]["record_id"], "T-1")
        self.assertEqual(audit["unconfirmed_dropped"], 3)
        self.assertTrue((clean_df["confirmation_status"] == "Confirmed").all())

    def test_06_data_cleaning_prunes_missing_and_invalid_data(self):
        """Validates that null GPS, missing critical attributes, out-of-bounds coords, and duplicates are pruned."""
        raw_mock = pd.DataFrame([
            # Valid record
            {"record_id": "V-1", "confirmation_status": "Confirmed", "district": "New Delhi", "police_station": "Connaught Place", "crime_category": "Snatching", "premises_type": "Market", "date": "2025-01-01", "hour": 12, "minute": 0, "latitude": 28.6328, "longitude": 77.2195},
            # Missing coordinates (NaN)
            {"record_id": "M-1", "confirmation_status": "Confirmed", "district": "New Delhi", "police_station": "Connaught Place", "crime_category": "Snatching", "premises_type": "Market", "date": "2025-01-01", "hour": 13, "minute": 0, "latitude": np.nan, "longitude": 77.2195},
            # Zero / placeholder coordinates
            {"record_id": "M-2", "confirmation_status": "Confirmed", "district": "New Delhi", "police_station": "Connaught Place", "crime_category": "Snatching", "premises_type": "Market", "date": "2025-01-01", "hour": 14, "minute": 0, "latitude": 0.0, "longitude": 0.0},
            # Out-of-bounds coordinates (outside Delhi NCT)
            {"record_id": "M-3", "confirmation_status": "Confirmed", "district": "New Delhi", "police_station": "Connaught Place", "crime_category": "Snatching", "premises_type": "Market", "date": "2025-01-01", "hour": 15, "minute": 0, "latitude": 32.5000, "longitude": 74.2000},
            # Missing critical attribute (district)
            {"record_id": "M-4", "confirmation_status": "Confirmed", "district": None, "police_station": "Connaught Place", "crime_category": "Snatching", "premises_type": "Market", "date": "2025-01-01", "hour": 16, "minute": 0, "latitude": 28.6328, "longitude": 77.2195},
            # Missing crime category
            {"record_id": "M-5", "confirmation_status": "Confirmed", "district": "New Delhi", "police_station": "Connaught Place", "crime_category": "", "premises_type": "Market", "date": "2025-01-01", "hour": 17, "minute": 0, "latitude": 28.6328, "longitude": 77.2195},
            # Duplicate of V-1
            {"record_id": "V-1", "confirmation_status": "Confirmed", "district": "New Delhi", "police_station": "Connaught Place", "crime_category": "Snatching", "premises_type": "Market", "date": "2025-01-01", "hour": 12, "minute": 0, "latitude": 28.6328, "longitude": 77.2195},
        ])
        clean_df, audit = clean_crime_dataset(raw_mock)
        self.assertEqual(len(clean_df), 1)
        self.assertEqual(clean_df.iloc[0]["record_id"], "V-1")
        self.assertEqual(clean_df.isnull().sum().sum(), 0)
        self.assertGreater(audit["missing_coords_dropped"], 0)
        self.assertGreater(audit["out_of_bounds_coords_dropped"], 0)
        self.assertGreater(audit["duplicates_dropped"], 0)

    def test_07_hotspot_engine_auto_cleaning(self):
        """Verifies HotspotClusterEngine automatically cleans dirty input before clustering."""
        dirty_mock = pd.DataFrame([
            {"record_id": f"C-{i}", "confirmation_status": "Confirmed" if i % 4 != 0 else "Pending Investigation", "district": "New Delhi", "police_station": "Connaught Place", "crime_category": "Snatching", "premises_type": "Market", "severity_score": 3, "risk_index": 0.6, "date": "2025-01-01", "hour": 12, "minute": 0, "latitude": 28.6328 + np.random.normal(0, 0.001), "longitude": 77.2195 + np.random.normal(0, 0.001)}
            for i in range(50)
        ])
        # Inject nulls
        dirty_mock.loc[0, "latitude"] = np.nan
        dirty_mock.loc[1, "longitude"] = np.nan
        
        engine = HotspotClusterEngine(eps_meters=600.0, min_samples=5)
        # Should fit cleanly without NaN / DBSCAN crash
        engine.fit(dirty_mock, clean_data=True)
        self.assertTrue(engine.fitted)
        self.assertIsNotNone(engine.cleaning_audit_)
        self.assertGreater(engine.cleaning_audit_["unconfirmed_dropped"], 0)

if __name__ == "__main__":
    unittest.main(verbosity=2)

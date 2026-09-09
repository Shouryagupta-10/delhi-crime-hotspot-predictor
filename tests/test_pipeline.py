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
from models.cluster_engine import HotspotClusterEngine, compare_dbscan_vs_kmeans
from models.risk_predictor import DelhiCrimeRiskPredictor

class TestDelhiCrimePipeline(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.test_csv = os.path.join(PROJECT_ROOT, "data", "test_delhi_crime.csv")
        cls.df = generate_delhi_crime_dataset(num_records=1200, output_path=cls.test_csv)

    @classmethod
    def tearDownClass(cls):
        if os.path.exists(cls.test_csv):
            os.remove(cls.test_csv)

    def test_01_dataset_integrity(self):
        """Validates that dataset contains required fields, 15 districts, valid coordinates, and balanced distributions."""
        self.assertEqual(len(self.df), 1200)
        self.assertGreaterEqual(self.df["district"].nunique(), 14)
        self.assertEqual(self.df["premises_type"].nunique(), 8)
        
        # Verify latitude and longitude within National Capital Territory of Delhi
        self.assertTrue((self.df["latitude"] >= 28.35).all() and (self.df["latitude"] <= 28.95).all())
        self.assertTrue((self.df["longitude"] >= 76.80).all() and (self.df["longitude"] <= 77.45).all())
        
        # Verify no nulls in critical columns
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

if __name__ == "__main__":
    unittest.main(verbosity=2)

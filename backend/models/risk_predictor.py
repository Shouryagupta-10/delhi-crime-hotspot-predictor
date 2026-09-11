"""
Supervised ML Risk Prediction Engine
Trains an XGBoost / Ensemble classifier to predict crime risk levels
across Delhi districts, premises types, and temporal windows.
Adheres to strict featurization ordering and evaluation best practices.
"""

import os
import joblib
import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.metrics import classification_report, roc_auc_score, confusion_matrix, f1_score
from sklearn.ensemble import GradientBoostingClassifier, RandomForestClassifier
try:
    from xgboost import XGBClassifier
    HAS_XGBOOST = True
except Exception:
    HAS_XGBOOST = False

try:
    from .cluster_engine import HotspotClusterEngine
except (ImportError, ValueError):
    from cluster_engine import HotspotClusterEngine

class DelhiCrimeRiskPredictor:
    def __init__(self, use_xgboost=True):
        self.use_xgboost = use_xgboost
        self.cluster_engine = HotspotClusterEngine(eps_meters=600.0, min_samples=18)
        self.pipeline = None
        self.feature_names = []
        self.metrics = {}
        self.is_trained = False

    def engineer_features(self, df: pd.DataFrame, fit_cluster=False) -> pd.DataFrame:
        """Transforms raw records into modeling features with cyclical time and spatial proximity."""
        data = df.copy()
        
        # 1. Cyclical time features
        data["sin_hour"] = np.sin(2 * np.pi * data["hour"] / 24.0)
        data["cos_hour"] = np.cos(2 * np.pi * data["hour"] / 24.0)
        
        # 2. Hotspot cluster proximity
        if fit_cluster:
            self.cluster_engine.fit(data)
            
        distances = []
        for _, row in data.iterrows():
            d = self.cluster_engine.get_distance_to_nearest_hotspot_km(row["latitude"], row["longitude"])
            distances.append(round(d, 3))
        data["dist_to_hotspot_km"] = distances
        
        return data

    def build_preprocessing_pipeline(self):
        """Constructs ColumnTransformer for strict independent fitting."""
        cat_features = ["district", "premises_type", "day_of_week"]
        num_features = ["hour", "sin_hour", "cos_hour", "is_weekend", "is_night", "is_rush_hour", "dist_to_hotspot_km", "latitude", "longitude"]
        
        preprocessor = ColumnTransformer(
            transformers=[
                ("num", StandardScaler(), num_features),
                ("cat", OneHotEncoder(handle_unknown="ignore", sparse_output=False), cat_features)
            ]
        )
        return preprocessor, num_features, cat_features

    def train_and_evaluate(self, csv_path: str):
        """End-to-end training, validation, and serialization following ML best practices."""
        df = pd.read_csv(csv_path)
        
        # Feature engineering
        engineered_df = self.engineer_features(df, fit_cluster=True)
        
        feature_cols = ["district", "premises_type", "day_of_week", "hour", "sin_hour", "cos_hour", 
                        "is_weekend", "is_night", "is_rush_hour", "dist_to_hotspot_km", "latitude", "longitude"]
        X = engineered_df[feature_cols]
        y = engineered_df["is_high_risk"]
        
        # Strict train-test split BEFORE fitting transformers
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.20, random_state=42, stratify=y
        )
        
        preprocessor, num_features, cat_features = self.build_preprocessing_pipeline()
        
        if self.use_xgboost and HAS_XGBOOST:
            try:
                classifier = XGBClassifier(
                    n_estimators=180,
                    max_depth=5,
                    learning_rate=0.08,
                    subsample=0.85,
                    colsample_bytree=0.85,
                    random_state=42,
                    eval_metric="logloss"
                )
            except Exception:
                classifier = GradientBoostingClassifier(
                    n_estimators=180,
                    max_depth=5,
                    learning_rate=0.08,
                    subsample=0.85,
                    random_state=42
                )
        else:
            classifier = GradientBoostingClassifier(
                n_estimators=180,
                max_depth=5,
                learning_rate=0.08,
                subsample=0.85,
                random_state=42
            )
            
        self.pipeline = Pipeline(steps=[
            ("preprocessor", preprocessor),
            ("classifier", classifier)
        ])
        
        # Fit on training data only
        self.pipeline.fit(X_train, y_train)
        self.is_trained = True
        
        # Predictions on unseen test data
        y_pred = self.pipeline.predict(X_test)
        y_prob = self.pipeline.predict_proba(X_test)[:, 1]
        
        # Evaluation metrics
        f1 = f1_score(y_test, y_pred)
        roc_auc = roc_auc_score(y_test, y_prob)
        cm = confusion_matrix(y_test, y_pred).tolist()
        report = classification_report(y_test, y_pred, output_dict=True)
        
        # Extract feature importances
        cat_encoder = self.pipeline.named_steps["preprocessor"].named_transformers_["cat"]
        cat_encoded_names = list(cat_encoder.get_feature_names_out(cat_features))
        all_features = num_features + cat_encoded_names
        
        raw_importances = self.pipeline.named_steps["classifier"].feature_importances_
        feature_importance_list = sorted(
            [{"feature": f, "importance": round(float(imp), 4)} for f, imp in zip(all_features, raw_importances)],
            key=lambda x: x["importance"],
            reverse=True
        )
        
        self.metrics = {
            "f1_score": round(float(f1), 4),
            "roc_auc": round(float(roc_auc), 4),
            "accuracy": round(float(report["accuracy"]), 4),
            "precision_high_risk": round(float(report["1"]["precision"]), 4),
            "recall_high_risk": round(float(report["1"]["recall"]), 4),
            "confusion_matrix": cm,
            "top_features": feature_importance_list[:12],
            "test_sample_size": len(y_test)
        }
        
        print("=== MODEL EVALUATION METRICS ===")
        print(f"Accuracy:  {self.metrics['accuracy']}")
        print(f"F1-Score:  {self.metrics['f1_score']}")
        print(f"ROC-AUC:   {self.metrics['roc_auc']}")
        print(f"Precision (High Risk): {self.metrics['precision_high_risk']}")
        print(f"Recall (High Risk):    {self.metrics['recall_high_risk']}")
        return self.metrics

    def predict_risk(self, district: str, premises_type: str, hour: int, day_of_week: str, lat: float, lon: float) -> dict:
        """Predicts real-time risk score, level, and recommendations for user query."""
        if not self.is_trained:
            raise RuntimeError("Model is not trained yet. Call train_and_evaluate first.")
            
        is_weekend = 1 if day_of_week in ["Saturday", "Sunday"] else 0
        is_night = 1 if (hour >= 22 or hour <= 5) else 0
        is_rush_hour = 1 if (hour in [8, 9, 10, 17, 18, 19, 20]) else 0
        sin_hour = np.sin(2 * np.pi * hour / 24.0)
        cos_hour = np.cos(2 * np.pi * hour / 24.0)
        dist_to_hotspot = self.cluster_engine.get_distance_to_nearest_hotspot_km(lat, lon)
        
        sample_df = pd.DataFrame([{
            "district": district,
            "premises_type": premises_type,
            "day_of_week": day_of_week,
            "hour": hour,
            "sin_hour": sin_hour,
            "cos_hour": cos_hour,
            "is_weekend": is_weekend,
            "is_night": is_night,
            "is_rush_hour": is_rush_hour,
            "dist_to_hotspot_km": dist_to_hotspot,
            "latitude": lat,
            "longitude": lon
        }])
        
        prob = float(self.pipeline.predict_proba(sample_df)[0, 1])
        
        if prob >= 0.60:
            level = "CRITICAL / HIGH RISK"
            color = "#EF4444"
            advisory = "Intensify PCR patrolling, activate CCTV corridor tracking, deploy anti-snatching motorcycle squad."
        elif prob >= 0.35:
            level = "MODERATE RISK"
            color = "#F59E0B"
            advisory = "Regular beat patrol vigilance, verify perimeter lighting, monitor crowded transit pedestrian exits."
        else:
            level = "LOW / NORMAL RISK"
            color = "#10B981"
            advisory = "Standard community policing, routine log checks, perimeter surveillance."
            
        return {
            "high_risk_probability": round(prob * 100.0, 1),
            "risk_level": level,
            "risk_color": color,
            "dist_to_hotspot_km": round(dist_to_hotspot, 2),
            "advisory": advisory,
            "temporal_factors": {
                "is_night": bool(is_night),
                "is_rush_hour": bool(is_rush_hour),
                "is_weekend": bool(is_weekend)
            }
        }

    def save(self, model_path: str):
        """Serializes the predictor bundle (pipeline, cluster engine, and metrics)."""
        os.makedirs(os.path.dirname(model_path), exist_ok=True)
        bundle = {
            "pipeline": self.pipeline,
            "cluster_engine": self.cluster_engine,
            "metrics": self.metrics,
            "is_trained": self.is_trained
        }
        joblib.dump(bundle, model_path)
        print(f"Saved trained model bundle to {model_path}")

    @classmethod
    def load(cls, model_path: str):
        """Loads serialized model bundle."""
        bundle = joblib.load(model_path)
        instance = cls()
        instance.pipeline = bundle["pipeline"]
        instance.cluster_engine = bundle["cluster_engine"]
        instance.metrics = bundle["metrics"]
        instance.is_trained = bundle["is_trained"]
        return instance

if __name__ == "__main__":
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    csv_file = os.path.join(base_dir, "data", "delhi_crime_records.csv")
    model_file = os.path.join(base_dir, "models", "saved_models.pkl")
    
    predictor = DelhiCrimeRiskPredictor(use_xgboost=True)
    predictor.train_and_evaluate(csv_file)
    predictor.save(model_file)

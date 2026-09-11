"""
Rakshak.ai - XGBoost Crime-Risk Classification Service
======================================================

This service trains and serves an XGBoost-based multiclass classification model
evaluating historical spatiotemporal crime risk patterns in Delhi.

Important Scope & Ethical Disclaimers:
--------------------------------------
- This model is a historical pattern-based risk classification prototype.
- It does NOT predict exact future crimes, nor does it guarantee where or when an incident will occur.
- It calculates the historical risk level (LOW, MEDIUM, HIGH) associated with a given location,
  time, day, month, and optional crime category.

Target Label Formulation (Historical Pattern Ground Truth):
-----------------------------------------------------------
Historical incidents in the 35,000-record dataset are categorized into three risk tiers based
on offense severity, peak-hour exposure (18:00 - 01:00), and weapon involvement:
    Risk Index = severity_score (1-5) + 0.5 * is_peak_hour + 0.5 * has_weapon

- LOW (Index <= 2.5): Minor non-violent offenses (pickpocketing, petty theft outside peak hours).
- MEDIUM (2.5 < Index <= 3.5): Moderate property crimes (burglary, daytime snatching, vehicle theft).
- HIGH (Index > 3.5): Violent crimes, armed offenses (robbery, assault with weapons, late-night high-severity).
"""

import time
import os
import numpy as np
import pandas as pd
from typing import Optional, Dict, Any, List
from sqlalchemy.orm import Session
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import accuracy_score, f1_score, precision_recall_fscore_support
from xgboost import XGBClassifier

from models import CrimeRecord

# District representative center coordinates for distance proximity fallback
DISTRICT_CENTROIDS = {
    "Central": (28.6432, 77.2140),
    "North": (28.6675, 77.2285),
    "South": (28.5600, 77.1900),
    "South West": (28.5750, 77.1900),
    "South East": (28.5600, 77.2600),
    "New Delhi": (28.6315, 77.2167),
    "Shahdara": (28.6469, 77.3160),
    "North East": (28.6698, 77.2773),
    "West": (28.6255, 77.0705),
    "East": (28.6280, 77.3000),
    "Outer": (28.7000, 77.0500),
    "Outer North": (28.7942, 77.0353),
    "Rohini": (28.7150, 77.1200),
    "Dwarka": (28.5921, 77.0460)
}


class CrimeRiskPredictor:
    """
    Singleton service encapsulating model training, metrics tracking, and real-time risk inference.
    """
    def __init__(self):
        self.model: Optional[XGBClassifier] = None
        self.le_district: LabelEncoder = LabelEncoder()
        self.le_crime_type: LabelEncoder = LabelEncoder()
        self.le_day: LabelEncoder = LabelEncoder()
        self.metrics: Dict[str, Any] = {}
        self.is_trained: bool = False
        self.training_time: float = 0.0
        self.total_records: int = 0
        self.train_size: int = 0
        self.test_size: int = 0
        self.district_priors: Dict[str, Dict[str, float]] = {}
        self.feature_names: List[str] = [
            "latitude", "longitude", "hour", "hour_sin", "hour_cos",
            "month", "month_sin", "month_cos", "year",
            "district_encoded", "crime_type_encoded", "day_encoded"
        ]

    def train_model(self, db: Session) -> Dict[str, Any]:
        """
        Loads the 35,000 crime records from SQLite, constructs features and target labels,
        and trains the XGBoost classifier with an 80/20 train/test split.
        """
        start_time = time.time()
        print("[*] Loading crime records from database for XGBoost training...")

        records = db.query(
            CrimeRecord.latitude,
            CrimeRecord.longitude,
            CrimeRecord.hour,
            CrimeRecord.day_of_week,
            CrimeRecord.month,
            CrimeRecord.year,
            CrimeRecord.district,
            CrimeRecord.crime_type,
            CrimeRecord.severity_score,
            CrimeRecord.weapon_used
        ).all()

        if not records:
            raise ValueError("No crime records found in database to train the model.")

        df = pd.DataFrame([
            {
                "latitude": r[0],
                "longitude": r[1],
                "hour": r[2],
                "day_of_week": r[3],
                "month": r[4],
                "year": r[5],
                "district": r[6],
                "crime_type": r[7],
                "severity_score": r[8],
                "weapon_used": r[9]
            }
            for r in records
        ])
        self.total_records = len(df)

        # 1. Target Label Creation (Composite Risk Index)
        # Peak crime hours in Delhi: 18:00 - 01:00
        is_peak_hour = df["hour"].isin([18, 19, 20, 21, 22, 23, 0, 1]).astype(int)
        has_weapon = (df["weapon_used"] == "Yes").astype(int)
        risk_index = df["severity_score"] + 0.5 * is_peak_hour + 0.5 * has_weapon

        # Target classes: 0 = LOW, 1 = MEDIUM, 2 = HIGH
        target = pd.cut(
            risk_index,
            bins=[-np.inf, 2.5, 3.5, np.inf],
            labels=[0, 1, 2]
        ).astype(int)

        # 2. Encode Categorical Features
        df["district_encoded"] = self.le_district.fit_transform(df["district"])
        df["crime_type_encoded"] = self.le_crime_type.fit_transform(df["crime_type"])
        df["day_encoded"] = self.le_day.fit_transform(df["day_of_week"])

        # 3. Cyclical Temporal Features
        df["hour_sin"] = np.sin(2 * np.pi * df["hour"] / 24.0)
        df["hour_cos"] = np.cos(2 * np.pi * df["hour"] / 24.0)
        df["month_sin"] = np.sin(2 * np.pi * df["month"] / 12.0)
        df["month_cos"] = np.cos(2 * np.pi * df["month"] / 12.0)

        # 4. Cache district-level crime priors for when crime_type is omitted
        priors_df = df.groupby(["district", "crime_type"]).size().unstack(fill_value=0)
        self.district_priors = priors_df.div(priors_df.sum(axis=1), axis=0).to_dict(orient="index")

        # 5. Stratified Train/Test Split (80/20)
        X = df[self.feature_names]
        y = target

        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.20, random_state=42, stratify=y
        )
        self.train_size = len(X_train)
        self.test_size = len(X_test)

        # 6. Fit XGBoost Classifier
        print(f"[*] Training XGBClassifier on {self.train_size:,} samples (evaluating on {self.test_size:,} test samples)...")
        self.model = XGBClassifier(
            n_estimators=100,
            max_depth=5,
            learning_rate=0.10,
            subsample=0.85,
            colsample_bytree=0.85,
            eval_metric="mlogloss",
            random_state=42,
            n_jobs=2
        )
        self.model.fit(X_train, y_train)
        self.training_time = round(time.time() - start_time, 3)

        # 7. Calculate Legitimate Evaluation Metrics on Unseen Test Split
        y_pred = self.model.predict(X_test)
        acc = float(accuracy_score(y_test, y_pred))
        macro_f1 = float(f1_score(y_test, y_pred, average="macro"))
        weighted_f1 = float(f1_score(y_test, y_pred, average="weighted"))
        prec, rec, f1, supp = precision_recall_fscore_support(y_test, y_pred, labels=[0, 1, 2])

        class_names = ["LOW", "MEDIUM", "HIGH"]
        class_metrics = {}
        for i, cname in enumerate(class_names):
            class_metrics[cname] = {
                "precision": round(float(prec[i]), 4),
                "recall": round(float(rec[i]), 4),
                "f1_score": round(float(f1[i]), 4),
                "test_support": int(supp[i])
            }

        # Feature importances
        importances = {
            col: round(float(imp), 4)
            for col, imp in zip(self.feature_names, self.model.feature_importances_)
        }
        sorted_importances = dict(sorted(importances.items(), key=lambda x: x[1], reverse=True))

        self.metrics = {
            "accuracy": round(acc, 4),
            "macro_f1": round(macro_f1, 4),
            "weighted_f1": round(weighted_f1, 4),
            "class_metrics": class_metrics,
            "feature_importances": sorted_importances,
            "evaluation_note": "Evaluated strictly on unseen holdout test split (20% = 7,000 records)."
        }
        self.is_trained = True

        print(f"[✓] XGBoost model trained successfully in {self.training_time}s! Test Accuracy: {acc*100:.2f}%, Macro F1: {macro_f1:.4f}")
        return self.get_model_info()

    def get_model_info(self) -> Dict[str, Any]:
        """
        Returns structured model metadata, parameters, and evaluation metrics.
        """
        return {
            "model_name": "Rakshak.ai XGBoost Crime-Risk Classifier",
            "model_type": "Gradient Boosted Decision Trees (XGBClassifier)",
            "algorithm": "XGBoost v3.4.1 (Multiclass Softmax)",
            "training_record_count": self.total_records,
            "training_test_split": f"80% train ({self.train_size:,} records), 20% test ({self.test_size:,} records)",
            "feature_list": self.feature_names,
            "risk_classes": ["LOW", "MEDIUM", "HIGH"],
            "training_methodology": (
                "Supervised risk classification trained on historical Delhi crime incidents (2015-2025). "
                "Target labels combine incident severity rating (1-5), circadian peak-hour vulnerability "
                "(18:00 - 01:00), and weapon involvement into a composite risk tier. Evaluated using "
                "stratified 80/20 holdout validation."
            ),
            "evaluation_metrics": self.metrics,
            "training_time_seconds": self.training_time,
            "model_status": "trained_and_ready" if self.is_trained else "pending_training"
        }

    def _infer_district_from_coords(self, lat: float, lon: float) -> str:
        """
        Finds the nearest Delhi district based on distance to known district centers.
        """
        best_district = "Central"
        min_dist = float("inf")
        for dist, (d_lat, d_lon) in DISTRICT_CENTROIDS.items():
            dist_sq = (lat - d_lat)**2 + (lon - d_lon)**2
            if dist_sq < min_dist:
                min_dist = dist_sq
                best_district = dist
        return best_district

    def predict_risk(
        self,
        db: Session,
        latitude: float,
        longitude: float,
        hour: int,
        day: str,
        month: int,
        year: int,
        district: Optional[str] = None,
        crime_type: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Performs inference to classify the historical crime risk of a given location/time coordinate.
        """
        if not self.is_trained:
            self.train_model(db)

        infer_start = time.time()

        # Normalize and validate inputs
        district_val = district.strip() if district else self._infer_district_from_coords(latitude, longitude)
        # Ensure district is recognized
        if district_val not in self.le_district.classes_:
            district_val = self._infer_district_from_coords(latitude, longitude)

        # Standardize day of week
        valid_days = list(self.le_day.classes_)
        day_normalized = day.strip().capitalize()
        if day_normalized not in valid_days:
            day_normalized = "Wednesday"  # Median/peak day default

        # Cyclical transformations
        hour_sin = np.sin(2 * np.pi * hour / 24.0)
        hour_cos = np.cos(2 * np.pi * hour / 24.0)
        month_sin = np.sin(2 * np.pi * month / 12.0)
        month_cos = np.cos(2 * np.pi * month / 12.0)

        district_enc = int(self.le_district.transform([district_val])[0])
        day_enc = int(self.le_day.transform([day_normalized])[0])

        class_names = ["LOW", "MEDIUM", "HIGH"]

        # Case A: Specific crime_type provided
        if crime_type and crime_type in self.le_crime_type.classes_:
            crime_type_enc = int(self.le_crime_type.transform([crime_type])[0])
            row_dict = {
                "latitude": latitude, "longitude": longitude,
                "hour": hour, "hour_sin": hour_sin, "hour_cos": hour_cos,
                "month": month, "month_sin": month_sin, "month_cos": month_cos,
                "year": year, "district_encoded": district_enc,
                "crime_type_encoded": crime_type_enc, "day_encoded": day_enc
            }
            sample_df = pd.DataFrame([row_dict])
            raw_probs = self.model.predict_proba(sample_df)[0]
            evaluated_type = crime_type

        # Case B: crime_type omitted -> calculate expected risk weighted by district crime priors
        else:
            priors = self.district_priors.get(district_val, {})
            accumulated_probs = np.zeros(3)

            for ctype in self.le_crime_type.classes_:
                weight = priors.get(ctype, 0.1)
                ctype_enc = int(self.le_crime_type.transform([ctype])[0])
                row_dict = {
                    "latitude": latitude, "longitude": longitude,
                    "hour": hour, "hour_sin": hour_sin, "hour_cos": hour_cos,
                    "month": month, "month_sin": month_sin, "month_cos": month_cos,
                    "year": year, "district_encoded": district_enc,
                    "crime_type_encoded": ctype_enc, "day_encoded": day_enc
                }
                sample_df = pd.DataFrame([row_dict])
                p = self.model.predict_proba(sample_df)[0]
                accumulated_probs += weight * p

            # Normalize probabilities
            total_weight = sum(priors.values()) if priors else 1.0
            raw_probs = accumulated_probs / total_weight
            evaluated_type = "Overall (Weighted across historical district offenses)"

        # Predicted class and confidence
        pred_idx = int(np.argmax(raw_probs))
        risk_level = class_names[pred_idx]
        confidence = round(float(raw_probs[pred_idx]), 4)

        # Risk score calibrated to a 0 - 100 continuous index
        # Weights: LOW = 15, MEDIUM = 55, HIGH = 95
        risk_score = round(float(raw_probs[0] * 15.0 + raw_probs[1] * 55.0 + raw_probs[2] * 95.0), 1)

        prob_dict = {
            "LOW": round(float(raw_probs[0]), 4),
            "MEDIUM": round(float(raw_probs[1]), 4),
            "HIGH": round(float(raw_probs[2]), 4)
        }

        # Contextual explanation of contributing factors
        contributing_factors = []
        is_peak = hour in [18, 19, 20, 21, 22, 23, 0, 1]
        if is_peak:
            contributing_factors.append(f"Hour {hour:02d}:00 falls within Delhi's peak evening/night crime window (18:00 - 01:00).")
        else:
            contributing_factors.append(f"Hour {hour:02d}:00 falls during lower-incidence daytime hours.")

        contributing_factors.append(f"Administrative district '{district_val}' with historical base coordinates ({latitude:.4f}, {longitude:.4f}).")

        if crime_type and crime_type in self.le_crime_type.classes_:
            contributing_factors.append(f"Specific offense profile evaluated: '{crime_type}'.")
        else:
            contributing_factors.append("Composite evaluation aggregating historical offense probabilities for this jurisdiction.")

        contributing_factors.append("Assessment based strictly on historical crime records, not an individual future event guarantee.")

        inference_time_ms = round((time.time() - infer_start) * 1000, 2)

        return {
            "risk_level": risk_level,
            "risk_score": risk_score,
            "confidence": confidence,
            "probabilities": prob_dict,
            "input_parameters": {
                "latitude": latitude,
                "longitude": longitude,
                "hour": hour,
                "day_of_week": day_normalized,
                "month": month,
                "year": year,
                "district": district_val,
                "crime_type": evaluated_type
            },
            "explanation": " ".join(contributing_factors),
            "inference_time_ms": inference_time_ms,
            "model_info": {
                "model_name": "Rakshak.ai XGBoost Crime-Risk Classifier",
                "algorithm": "XGBoost (Multiclass)",
                "classes": class_names
            }
        }


# Global singleton instance
predictor_service = CrimeRiskPredictor()

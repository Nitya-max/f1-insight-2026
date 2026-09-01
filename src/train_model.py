import pandas as pd
import numpy as np
import joblib
import os
from xgboost import XGBClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, classification_report

print("🤖 Training Pre-Race Winner Prediction Model...")

data_path = "data/processed/f1_features.csv"
if not os.path.exists(data_path):
    raise FileNotFoundError(f"Missing {data_path}. Please run preprocess.py first.")

df = pd.read_csv(data_path)

# Select Predictive Features
feature_cols = ['grid_clean', 'grid_delta', 'driver_recent_form', 'team_recent_form', 'team', 'circuit']
X_raw = df[feature_cols]
y = df['is_winner']

# One-hot encode Categorical Columns (Team and Circuit)
X = pd.get_dummies(X_raw, columns=['team', 'circuit'], drop_first=True)

# Split Train & Test
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)

# Train XGBoost Classifier
model = XGBClassifier(
    n_estimators=150,
    max_depth=4,
    learning_rate=0.05,
    scale_pos_weight=19,  # Balances 1 winner per 19 non-winners
    eval_metric='logloss',
    random_state=42
)
model.fit(X_train, y_train)

# Evaluation
y_pred = model.predict(X_test)
acc = accuracy_score(y_test, y_pred)
print(f"✓ Binary Classification Accuracy: {acc * 100:.2f}%")

# Save the Model Artifact and Expected Column Mapping
os.makedirs("models", exist_ok=True)
joblib.dump({"model": model, "feature_columns": X.columns.tolist()}, "models/f1_winner_model.pkl")
print("✅ Saved trained model artifact to 'models/f1_winner_model.pkl'")
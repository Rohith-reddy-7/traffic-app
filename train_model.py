import pandas as pd
import pickle
from xgboost import XGBRegressor
from sklearn.preprocessing import StandardScaler
import os

# Create models directory if it doesn't exist
os.makedirs('models', exist_ok=True)

# Load data
print("Loading traffic data...")
df = pd.read_csv('data/traffic.csv')

# Display basic info
print(f"Dataset shape: {df.shape}")
print(f"Columns: {df.columns.tolist()}")
print(f"First few rows:\n{df.head()}")

# Convert datetime to datetime object
df['datetime'] = pd.to_datetime(df['datetime'])

# Feature Engineering
print("\nEngineering features...")
df['hour'] = df['datetime'].dt.hour
df['day'] = df['datetime'].dt.day
df['month'] = df['datetime'].dt.month
df['weekday'] = df['datetime'].dt.weekday  # 0=Monday, 6=Sunday
df['is_weekend'] = (df['weekday'] >= 5).astype(int)  # 1 if Saturday or Sunday

# Display engineered features
print(f"Features after engineering:\n{df.head()}")

# Prepare training data
feature_columns = ['junction_id', 'hour', 'day', 'month', 'weekday', 'is_weekend']
X = df[feature_columns]
y = df['vehicle_count']

print(f"\nTraining features shape: {X.shape}")
print(f"Target shape: {y.shape}")

# Train XGBoost model
print("\nTraining XGBoost model...")
model = XGBRegressor(
    n_estimators=100,
    max_depth=6,
    learning_rate=0.1,
    subsample=0.8,
    colsample_bytree=0.8,
    random_state=42
)

model.fit(X, y)

# Calculate R² score for reference
train_score = model.score(X, y)
print(f"Model R² Score: {train_score:.4f}")

# Save the model
print("\nSaving model...")
with open('models/traffic_model.pkl', 'wb') as f:
    pickle.dump(model, f)
print("Model saved to models/traffic_model.pkl")

# Save feature columns to avoid feature mismatch errors
with open('models/model_features.pkl', 'wb') as f:
    pickle.dump(feature_columns, f)
print("Feature columns saved to models/model_features.pkl")

print("\nTraining complete!")
print(f"Model saved successfully. Ready for predictions.")

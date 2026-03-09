"""
Multi-City Traffic Model Training
Train a single model on traffic data from multiple metropolitan cities
"""

import pandas as pd
import numpy as np
from xgboost import XGBRegressor
from sklearn.preprocessing import LabelEncoder
import pickle
import glob
import os

def load_all_city_data():
    """
    Load and combine traffic data from all cities
    """
    print('╔' + '═'*60 + '╗')
    print('║' + ' '*12 + '🚀 Multi-City Model Training' + ' '*20 + '║')
    print('╚' + '═'*60 + '╝\n')
    
    all_dfs = []
    city_files = glob.glob('data/*_traffic.csv')
    
    if not city_files:
        print("❌ No city data files found!")
        print("   Run: python fetch_multi_city_data.py")
        return None
    
    print(f"📂 Found {len(city_files)} city data files:")
    
    for file in sorted(city_files):
        city_name = os.path.basename(file).replace('_traffic.csv', '')
        try:
            df = pd.read_csv(file)
            all_dfs.append(df)
            print(f"   ✅ {city_name.upper()}: {len(df)} records")
        except Exception as e:
            print(f"   ❌ {city_name}: {e}")
    
    if not all_dfs:
        return None
    
    # Combine all data
    combined_df = pd.concat(all_dfs, ignore_index=True)
    print(f"\n📊 Combined Dataset:")
    print(f"   Total Records: {len(combined_df)}")
    print(f"   Unique Cities: {combined_df['city'].nunique()}")
    print(f"   Date Range: {combined_df['datetime'].min()} to {combined_df['datetime'].max()}")
    print(f"   Vehicle Range: {combined_df['vehicle_count'].min()}-{combined_df['vehicle_count'].max()}")
    
    return combined_df

def prepare_features(df):
    """
    Engineer features for multi-city model
    """
    print(f"\n🔧 Feature Engineering...")
    
    df['datetime'] = pd.to_datetime(df['datetime'])
    
    # Time-based features
    df['hour'] = df['datetime'].dt.hour
    df['day'] = df['datetime'].dt.day
    df['month'] = df['datetime'].dt.month
    df['weekday'] = df['datetime'].dt.weekday
    df['is_weekend'] = (df['weekday'] >= 5).astype(int)
    
    # Encode city name
    city_encoder = LabelEncoder()
    df['city_encoded'] = city_encoder.fit_transform(df['city'])
    
    # Junction features
    junction_encoder = LabelEncoder()
    df['junction_encoded'] = junction_encoder.fit_transform(df[['city', 'junction_id']].astype(str).agg('_'.join, axis=1))
    
    # Select features
    feature_columns = ['city_encoded', 'junction_encoded', 'hour', 'day', 'month', 'weekday', 'is_weekend']
    
    print(f"   ✅ Created {len(feature_columns)} features")
    print(f"   Features: {feature_columns}")
    
    return df, feature_columns, city_encoder, junction_encoder

def train_model(X, y):
    """
    Train XGBoost model on multi-city data
    """
    print(f"\n🤖 Training XGBoost Model...")
    print(f"   Dataset Shape: {X.shape}")
    print(f"   Training Samples: {len(X)}")
    
    model = XGBRegressor(
        n_estimators=200,
        max_depth=8,
        learning_rate=0.1,
        subsample=0.8,
        colsample_bytree=0.8,
        random_state=42,
        verbose=0
    )
    
    model.fit(X, y)
    
    # Calculate R² score
    train_score = model.score(X, y)
    
    print(f"   ✅ Model Training Complete")
    print(f"   R² Score: {train_score:.4f}")
    print(f"   Model Parameters:")
    print(f"      - Trees: 200")
    print(f"      - Max Depth: 8")
    print(f"      - Learning Rate: 0.1")
    
    return model

def save_models(model, feature_columns, city_encoder, junction_encoder):
    """
    Save model and encoders
    """
    print(f"\n💾 Saving Models...")
    
    os.makedirs('models', exist_ok=True)
    
    # Save model
    with open('models/traffic_model_multicity.pkl', 'wb') as f:
        pickle.dump(model, f)
    
    # Save feature columns
    with open('models/model_features_multicity.pkl', 'wb') as f:
        pickle.dump(feature_columns, f)
    
    # Save encoders
    with open('models/city_encoder.pkl', 'wb') as f:
        pickle.dump(city_encoder, f)
    
    with open('models/junction_encoder.pkl', 'wb') as f:
        pickle.dump(junction_encoder, f)
    
    print(f"   ✅ traffic_model_multicity.pkl")
    print(f"   ✅ model_features_multicity.pkl")
    print(f"   ✅ city_encoder.pkl")
    print(f"   ✅ junction_encoder.pkl")

def main():
    # Load data
    df = load_all_city_data()
    if df is None:
        return
    
    # Prepare features
    df, feature_columns, city_encoder, junction_encoder = prepare_features(df)
    
    # Prepare training data
    X = df[feature_columns]
    y = df['vehicle_count']
    
    # Train model
    model = train_model(X, y)
    
    # Save models
    save_models(model, feature_columns, city_encoder, junction_encoder)
    
    print('\n' + '═'*62)
    print("✅ MULTI-CITY MODEL TRAINING COMPLETE!")
    print('═'*62)
    print("\n📌 Next Steps:")
    print("   Run: streamlit run app_multi_city.py")
    print('═'*62)

if __name__ == "__main__":
    main()

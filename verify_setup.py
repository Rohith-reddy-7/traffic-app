"""
Verification Script for Smart City Traffic System
Run this to check if all requirements are met before running the main scripts
"""

import sys
import os
from pathlib import Path

print("=" * 60)
print("🔍 Smart City Traffic System - Setup Verification")
print("=" * 60)

# Check Python version
print("\n1️⃣ Python Version Check:")
print(f"   Python Version: {sys.version.split()[0]}")
if sys.version_info >= (3, 8):
    print("   ✅ Python 3.8+ detected (Required)")
else:
    print("   ❌ Python 3.8+ required")

# Check directory structure
print("\n2️⃣ Directory Structure Check:")
required_dirs = ['data', 'models']
for dir_name in required_dirs:
    path = Path(dir_name)
    if path.exists() and path.is_dir():
        print(f"   ✅ {dir_name}/ exists")
    else:
        print(f"   ❌ {dir_name}/ missing")

# Check files
print("\n3️⃣ Required Files Check:")
required_files = {
    'data/traffic.csv': 'Training dataset',
    'train_model.py': 'Model training script',
    'app.py': 'Streamlit dashboard',
    'requirements.txt': 'Dependencies list'
}

for file_path, description in required_files.items():
    path = Path(file_path)
    if path.exists():
        size = path.stat().st_size
        print(f"   ✅ {file_path:<20} ({size:>7} bytes) - {description}")
    else:
        print(f"   ❌ {file_path:<20} MISSING - {description}")

# Check data file
print("\n4️⃣ Dataset Validation:")
try:
    import pandas as pd
    df = pd.read_csv('data/traffic.csv')
    print(f"   ✅ Dataset loaded successfully")
    print(f"      • Records: {len(df)}")
    print(f"      • Columns: {', '.join(df.columns.tolist())}")
    print(f"      • Junctions: {df['junction_id'].unique().tolist()}")
    print(f"      • Date Range: {df['datetime'].min()} to {df['datetime'].max()}")
except Exception as e:
    print(f"   ❌ Error loading dataset: {e}")

# Check dependencies
print("\n5️⃣ Python Dependencies Check:")
dependencies = {
    'streamlit': '1.28.1+',
    'pandas': '2.0.0+',
    'numpy': '1.24.0+',
    'xgboost': '2.0.0+',
    'sklearn': '1.3.0+',
    'plotly': '5.17.0+'
}

missing_packages = []
for package, min_version in dependencies.items():
    try:
        if package == 'sklearn':
            __import__('sklearn')
            print(f"   ✅ scikit-learn")
        else:
            __import__(package)
            print(f"   ✅ {package}")
    except ImportError:
        print(f"   ❌ {package} NOT installed")
        missing_packages.append(package)

# Installation guide
if missing_packages:
    print("\n" + "=" * 60)
    print("📦 Missing Dependencies Detected!")
    print("=" * 60)
    print("\nTo install missing packages, run:")
    print("   pip install -r requirements.txt")
    print("=" * 60)
else:
    print("\n" + "=" * 60)
    print("✅ All Dependencies Installed!")
    print("=" * 60)

# Verification Summary
print("\n6️⃣ Verification Summary:")
print("""
   To get started:
   
   Step 1: Install Dependencies
   └─ pip install -r requirements.txt
   
   Step 2: Train the Model
   └─ python train_model.py
      (This will create models/traffic_model.pkl)
   
   Step 3: Launch Dashboard
   └─ streamlit run app.py
      (Opens at http://localhost:8501)
""")

print("=" * 60)
print("Ready to begin? Run: python train_model.py")
print("=" * 60)

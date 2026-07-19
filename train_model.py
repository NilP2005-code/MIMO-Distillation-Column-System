import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report, roc_auc_score

def engineer_fault_features(df):
    """
    Engineers features using column position indices instead of string keys
    to eliminate MATLAB naming discrepancies.
    """
    # Force column renaming based on position order:
    # Index 0: Time, Index 1: Temp, Index 2: Steam_PID, Index 3: Valve_Status, Index 4: Distillate_Purity
    df.columns = ['Time', 'Temperature', 'Steam_PID', 'Valve_Status', 'Distillate_Purity'] + list(df.columns[5:])
    
    # 1. Calculate Valve Stiction Index (Deviation between PID request and actual valve position)
    df['valve_deviation'] = np.abs(df['Steam_PID'] - df['Valve_Status'])
    
    # 2. Rolling window features to catch exponential thermal runaway signatures
    df['temp_rolling_mean'] = df['Temperature'].rolling(window=30, min_periods=1).mean()
    df['temp_rolling_std']  = df['Temperature'].rolling(window=30, min_periods=1).std()
    
    # 3. Calculate Rate of Change (Gradient) for Temperature
    df['temp_gradient'] = np.gradient(df['Temperature'])
    
    return df

# --- 1. Data Ingestion & Preprocessing ---
# Load telemetry exported from the Simulink simulation workspace
try:
    data = pd.read_csv('distillation_column_telemetry.csv')
except FileNotFoundError:
    # Synthesize dummy dataframe matching Simulink export structural template for testing
    print("Telemetry file not found. Generating synthetic simulation data for validation...")
    timesteps = 5000
    np.random.seed(42)
    data = pd.DataFrame({
        'time': np.arange(timesteps),
        'temp': 80 + np.random.normal(0, 0.5, timesteps) + (np.arange(timesteps) * 0.006), # simulated drift
        'pressure': 2.1 + np.random.normal(0, 0.02, timesteps),
        'pid_out_V': 45.0 + np.sin(np.arange(timesteps)/50) * 5,
        'actual_valve_V': 45.0 + np.sin(np.arange(timesteps)/50) * 5
    })
    # Inject a simulated valve stiction error causing thermal runaway near the end
    data.loc[4000:, 'actual_valve_V'] = data.loc[4000, 'actual_valve_V'] 
    data.loc[4200:, 'temp'] += (data.loc[4200:, 'time'] - 4200) * 0.15 
    
    # Create Ground Truth Label (1 = Safety Trip condition active / imminent within 15 mins)
    data['target_trip'] = np.where(data['temp'] > 110, 1, 0)
data = pd.read_csv('distillation_column_telemetry.csv')

# --- Add this line here to check your columns ---
print("ACTUAL CSV COLUMNS FOUND:", list(data.columns))
# Apply operational feature engineering pipeline
processed_data = engineer_fault_features(data)

# --- 2. Feature Selection & Data Splitting ---
processed_data = engineer_fault_features(data)

# Extract engineered inputs for the ML model
features = ['Temperature', 'valve_deviation', 'temp_rolling_mean', 
            'temp_rolling_std', 'temp_gradient']

X = processed_data[features]

# Create ground truth classification targets based on the 120°C safety trip condition
y = np.where(processed_data['Temperature'] > 120, 1, 0)

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)

# --- 3. Model Training (Predictive Anomaly Detection) ---
model = RandomForestClassifier(n_estimators=100, max_depth=8, random_state=42)
model.fit(X_train, y_train)

# --- 4. Performance Diagnostics ---
# Ensure the model generates predictions on the test features
predictions = model.predict(X_test)

# Try-except block to handle probabilities safely (from the previous step)
try:
    probabilities = model.predict_proba(X_test)[:, 1]
except IndexError:
    probabilities = np.zeros(X_test.shape[0])

# This print statement will now execute successfully
print("\n=== Model Evaluation Metrics Summary ===")
print(classification_report(y_test, predictions, zero_division=0))

# Only calculate ROC AUC if both normal and trip classes exist in the test split
if len(np.unique(y_test)) > 1:
    print(f"ROC AUC Score: {roc_auc_score(y_test, probabilities):.4f}")
else:
    print("ROC AUC Score: Not defined (Only 1 operational class present in test data)")
print(classification_report(y_test, predictions))
print(f"ROC AUC Score: {roc_auc_score(y_test, probabilities):.4f}")
# --- 5. Deployable Feature Importance Extraction ---
importances = pd.Series(model.feature_importances_, index=features).sort_values(ascending=False)
print("\n=== Feature Importance Matrix (Key Indicators Assessed) ===")
print(importances)
import pandas as pd
import numpy as np
import joblib
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_squared_error, r2_score, mean_absolute_error
from sklearn.preprocessing import LabelEncoder, StandardScaler
from pathlib import Path

# Configuration
BASE_DIR = Path(__file__).parent
DATA_PATH = BASE_DIR / "data/tomates_annuel_dataset.csv"
MODEL_DIR = BASE_DIR / "models"
MODEL_DIR.mkdir(parents=True, exist_ok=True)

print("="*60)
print("🌱 POTAG'IA - ENTRAÎNEMENT ANNUEL ROBUSTE")
print("="*60)

# 1. Chargement et conversion des dates
df = pd.read_csv(DATA_PATH)
df['Date'] = pd.to_datetime(df['Date'])
df = df.sort_values('Date')

# Feature Engineering
df['Mois'] = df['Date'].dt.month
df['Diff_Temp'] = df['Temp_Air_Moy'] - df['Temp_Sol']
df['Sol_Chaud'] = (df['Temp_Sol'] >= 12).astype(int)
df['Gel_Risque'] = (df['Temp_Air_Moy'] < 5).astype(int)
df['Ratio_NP'] = df['N'] / (df['P'] + 0.1)
df['Ratio_NK'] = df['N'] / (df['K'] + 0.1)

# Encodage Variété
le_variete = LabelEncoder()
df['Variete_Encoded'] = le_variete.fit_transform(df['Variete'])

# Sélection des features
features = [
    'Variete_Encoded', 'Temp_Air_Moy', 'Temp_Sol', 'Humidite_Sol', 
    'N', 'P', 'K', 'Prevision_Gelee', 'Mois', 
    'Diff_Temp', 'Sol_Chaud', 'Gel_Risque', 'Ratio_NP', 'Ratio_NK'
]

X = df[features]
y = df['Indice_Succes']

# Normalisation
scaler = StandardScaler()
X_scaled = pd.DataFrame(scaler.fit_transform(X), columns=features)

# 2. SPLIT TEMPOREL (75% Train, 25% Test)
split_idx = int(len(df) * 0.75)
X_train, X_test = X_scaled.iloc[:split_idx], X_scaled.iloc[split_idx:]
y_train, y_test = y.iloc[:split_idx], y.iloc[split_idx:]

print(f"   ✓ Entraînement : {len(X_train)} lignes")
print(f"   ✓ Test : {len(X_test)} lignes")

# 3. Entraînement
model = RandomForestRegressor(n_estimators=100, max_depth=8, min_samples_leaf=10, random_state=42, n_jobs=-1)
model.fit(X_train, y_train)

# 4. Évaluation
preds = model.predict(X_test)
mae = mean_absolute_error(y_test, preds)
r2 = r2_score(y_test, preds)

print(f"\n📊 PERFORMANCES :")
print(f"   R² Score : {r2:.4f}")
print(f"   MAE      : {mae:.2f} points")

# Sauvegarde des métriques par variété pour la fiabilité
varietes = df['Variete'].unique()
scores_mae_v = {}
for var in varietes:
    idx = df[df['Variete'] == var].index
    # On ne prend que les indices qui sont dans le test set
    idx_test = [i for i in idx if i >= split_idx]
    if idx_test:
        v_test_X = X_scaled.loc[idx_test]
        v_test_y = y.loc[idx_test]
        v_preds = model.predict(v_test_X)
        scores_mae_v[var] = float(mean_absolute_error(v_test_y, v_preds))

perf_metrics = {
    "global_mae": float(mae),
    "variete_mae": scores_mae_v,
    "timestamp": pd.Timestamp.now().isoformat()
}

# 5. Sauvegarde des artifacts
joblib.dump(model, MODEL_DIR / "modele_potagia.joblib") # On écrase l'ancien pour la liaison app
joblib.dump(le_variete, MODEL_DIR / "encodeur_varietes.joblib")
joblib.dump(scaler, MODEL_DIR / "scaler.joblib")
joblib.dump(features, MODEL_DIR / "features_list.joblib")
joblib.dump(perf_metrics, MODEL_DIR / "performance.joblib")

print(f"\n✅ Modèle annuel prêt et déployé dans {MODEL_DIR}")

import joblib
import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import LabelEncoder, StandardScaler
from sklearn.metrics import mean_squared_error, r2_score, mean_absolute_error
from pathlib import Path

# ==========================================
# POTAG'IA - SYSTÈME D'IA PRÉDICTIF
# ==========================================

print("="*60)
print("🌱 POTAG'IA - SYSTÈME D'INTELLIGENCE ARTIFICIELLE")
print("="*60)

BASE_DIR = Path(__file__).parent
DATA_DIR = BASE_DIR / "data"
MODEL_DIR = BASE_DIR / "models"
MODEL_DIR.mkdir(parents=True, exist_ok=True)

# 1. Chargement
df_tomates = pd.read_csv(DATA_DIR / "tomates_dataset.csv")
df_soil = pd.read_csv(DATA_DIR / "soil_quality_dataset.csv")

# Encodage
le_variete = LabelEncoder()
df_tomates['Variete_Encoded'] = le_variete.fit_transform(df_tomates['Variete'])
le_soil = LabelEncoder()
df_soil['Soil_Type_Encoded'] = le_soil.fit_transform(df_soil['Soil_Type'])

# Fusion simple
df_tomates['soil_index'] = np.arange(len(df_tomates)) % len(df_soil)
df_merged = df_tomates.merge(df_soil, left_on='soil_index', right_index=True, how='left')

# ==========================================
# 2. FEATURE ENGINEERING
# ==========================================
print("\n3. Feature Engineering...")
df_merged['Diff_Temp'] = df_merged['Temp_Air_Moy'] - df_merged['Temp_Sol']
df_merged['Sol_Chaud'] = (df_merged['Temp_Sol'] >= 12).astype(int)
df_merged['Gel_Risque'] = (df_merged['Temp_Air_Moy'] < 5).astype(int)
df_merged['Ratio_NP'] = df_merged['N'] / (df_merged['P'] + 0.1)
df_merged['Ratio_NK'] = df_merged['N'] / (df_merged['K'] + 0.1)

# Règle métier : Gelée prévue -> Succès = 0
df_merged.loc[df_merged['Prevision_Gelee'] == 1, 'Indice_Succes'] = 0

features_finales = [
    'Variete_Encoded', 'Temp_Air_Moy', 'Temp_Sol', 'Humidite_Sol', 
    'N', 'P', 'K', 'Prevision_Gelee', 'PH_Level', 'Organic_Matter', 
    'Moisture_Content', 'Soil_Type_Encoded',
    'Diff_Temp', 'Sol_Chaud', 'Gel_Risque', 'Ratio_NP', 'Ratio_NK'
]

X = df_merged[features_finales].fillna(df_merged[features_finales].mean())
y = df_merged['Indice_Succes']

# Normalisation
scaler = StandardScaler()
X_scaled = pd.DataFrame(scaler.fit_transform(X), columns=features_finales)

# ==========================================
# 3. VALIDATION PAR VARIÉTÉ (LOVO)
# ==========================================
print("\n4. Évaluation par Variété (Leave-One-Variety-Out)...")
varietes = df_merged['Variete'].unique()
scores_mae = []

for var in varietes:
    train_idx = df_merged[df_merged['Variete'] != var].index
    test_idx = df_merged[df_merged['Variete'] == var].index
    
    X_train_v, X_test_v = X_scaled.iloc[train_idx], X_scaled.iloc[test_idx]
    y_train_v, y_test_v = y.iloc[train_idx], y.iloc[test_idx]
    
    tmp_model = RandomForestRegressor(n_estimators=50, max_depth=6, random_state=42, n_jobs=-1)
    tmp_model.fit(X_train_v, y_train_v)
    
    mae = mean_absolute_error(y_test_v, tmp_model.predict(X_test_v))
    scores_mae.append(mae)
    print(f"      - {var:18}: MAE = {mae:.2f}")

print(f"\n📊 MAE MOYEN (LOVO): {np.mean(scores_mae):.2f} points")

# Sauvegarde des performances pour la fiabilité
perf_metrics = {
    "global_mae": float(np.mean(scores_mae)),
    "variete_mae": {var: float(mae) for var, mae in zip(varietes, scores_mae)},
    "timestamp": pd.Timestamp.now().isoformat()
}
joblib.dump(perf_metrics, MODEL_DIR / "performance.joblib")

# ==========================================
# 4. ENTRAÎNEMENT FINAL & SAUVEGARDE
# ==========================================
print("\n5. Entraînement final...")
model = RandomForestRegressor(n_estimators=100, max_depth=7, min_samples_leaf=15, random_state=42, n_jobs=-1)
model.fit(X_scaled, y)

# Vérif Overfitting
train_mae = mean_absolute_error(y, model.predict(X_scaled))
print(f"   ✓ Train MAE: {train_mae:.2f} (comparer avec LOVO MAE)")

joblib.dump(model, MODEL_DIR / "modele_potagia.joblib")
joblib.dump(le_variete, MODEL_DIR / "encodeur_varietes.joblib")
joblib.dump(le_soil, MODEL_DIR / "encodeur_sols.joblib")
joblib.dump(scaler, MODEL_DIR / "scaler.joblib")
joblib.dump(features_finales, MODEL_DIR / "features_list.joblib")
print("   ✓ Modèle et artifacts sauvegardés.")

# ==========================================
# 5. FONCTIONS DE PRÉDICTION
# ==========================================

def obtenir_recommandation(score, prevision_gelee):
    if prevision_gelee == 1 or score < 40:
        return "❌ ATTENDRE", "Risque de gel ou conditions défavorables."
    if score < 65:
        return "⚠️ RISQUÉ", "Conditions moyennes. Protection conseillée."
    if score < 85:
        return "✅ FAVORABLE", "Bonnes conditions de plantation."
    return "🌟 IDÉAL", "Conditions parfaites ! Plantez maintenant."

def predire_succes_plantation(variete, temp_air, temp_sol, humidite_sol, 
                             azote_n, phosphore_p, potassium_k, 
                             prevision_gelee, ph_sol, matiere_organique, 
                             humidite_soil, soil_type):
    try:
        # Encodage manuel pour le test
        var_enc = le_variete.transform([variete])[0]
        soil_enc = le_soil.transform([soil_type])[0]
        
        data = {
            'Variete_Encoded': var_enc, 'Temp_Air_Moy': temp_air, 'Temp_Sol': temp_sol,
            'Humidite_Sol': humidite_sol, 'N': azote_n, 'P': phosphore_p, 'K': potassium_k,
            'Prevision_Gelee': prevision_gelee, 'PH_Level': ph_sol, 'Organic_Matter': matiere_organique,
            'Moisture_Content': humidite_soil, 'Soil_Type_Encoded': soil_enc,
            'Diff_Temp': temp_air - temp_sol, 'Sol_Chaud': 1 if temp_sol >= 12 else 0,
            'Gel_Risque': 1 if temp_air < 5 else 0, 'Ratio_NP': azote_n/(phosphore_p+0.1),
            'Ratio_NK': azote_n/(potassium_k+0.1)
        }
        
        X_test = pd.DataFrame([data])[features_finales]
        X_test_scaled = scaler.transform(X_test)
        
        score = float(model.predict(X_test_scaled)[0])
        if prevision_gelee == 1: score = 0
        
        statut, conseil = obtenir_recommandation(score, prevision_gelee)
        return {"score": round(score, 2), "statut": statut, "conseil": conseil}
    except Exception as e:
        return {"error": str(e)}

# TEST
print("\n🧪 TEST FINAL (Marmande - Optimal):")
res = predire_succes_plantation("Marmande", 25, 22, 70, 110, 80, 150, 0, 6.8, 5.0, 70, "Loamy")
print(f"   Résultat: {res}")

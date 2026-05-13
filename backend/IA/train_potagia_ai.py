import joblib
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import LabelEncoder, StandardScaler
from sklearn.metrics import mean_squared_error, r2_score, mean_absolute_error
from pathlib import Path

# ==========================================
# POTAG'IA - SYSTÈME D'IA PRÉDICTIF
# Prédiction de l'indice de succès de plantation
# ==========================================

print("="*60)
print("🌱 POTAG'IA - SYSTÈME D'INTELLIGENCE ARTIFICIELLE")
print("="*60)

# Configuration des chemins
BASE_DIR = Path(__file__).parent
DATA_DIR = BASE_DIR / "data"
MODEL_DIR = BASE_DIR / "models"
MODEL_DIR.mkdir(parents=True, exist_ok=True)

print("\n1. Chargement des données...")
# Charger les datasets
df_tomates = pd.read_csv(DATA_DIR / "tomates_dataset.csv")
df_soil = pd.read_csv(DATA_DIR / "soil_quality_dataset.csv")

# Essayer de charger les données météo temps réel
meteo_file = DATA_DIR / "donnees_meteo_temps_reel.csv"
if meteo_file.exists():
    print(f"   ✓ Tomates dataset: {len(df_tomates)} lignes")
    print(f"   ✓ Sol dataset: {len(df_soil)} lignes")
    print(f"   ✓ Données météo temps réel trouvées!")
else:
    print(f"   ⚠️  Données météo temps réel non trouvées")
    print(f"   💡 Lance d'abord: python conversionJSONPourIA.py")

print("\n📋 DIAGNOSTIQUE DÉTAILLÉ DES DONNÉES:")
print(f"\n   🍅 TOMATES DATASET:")
print(f"      Total lignes: {len(df_tomates)}")
print(f"      Colonnes: {list(df_tomates.columns)}")
print(f"      Colonnes manquantes: {[c for c in ['Variete', 'Temp_Air_Moy', 'Temp_Sol', 'Humidite_Sol', 'N', 'P', 'K', 'Prevision_Gelee', 'Indice_Succes'] if c not in df_tomates.columns]}")

print(f"\n   🌍 SOL DATASET:")
print(f"      Total lignes: {len(df_soil)}")
print(f"      Colonnes: {list(df_soil.columns)}")
print(f"      Colonnes manquantes: {[c for c in ['Soil_Type', 'PH_Level', 'Organic_Matter', 'Moisture_Content'] if c not in df_soil.columns]}")

# ==========================================
# LE SAUVEUR DE RAM EST ICI
# ==========================================
print("\n1.5. Échantillonnage des données (gestion optimale de la RAM)...")
# Utiliser toutes les données disponibles pour l'entraînement (désactiver l'échantillonnage)
print(f"   ✓ Utilisation de toutes les lignes de `tomates_dataset.csv`: {len(df_tomates)} lignes")

print("\n2. Préparation des données pour l'Intelligence Artificielle...")

# ==========================================
# ENCODAGE DES VARIABLES CATÉGORIELLES
# ==========================================

# Encoder la variété de tomate
le_variete = LabelEncoder()
df_tomates['Variete_Encoded'] = le_variete.fit_transform(df_tomates['Variete'])
noms_varietes = le_variete.classes_
print(f"   ✓ Variétés reconnues: {list(noms_varietes)}")

# Encoder le type de sol
le_soil = LabelEncoder()
df_soil['Soil_Type_Encoded'] = le_soil.fit_transform(df_soil['Soil_Type'])
noms_sols = le_soil.classes_
print(f"   ✓ Types de sol reconnus: {list(noms_sols)}")

# ==========================================
# FUSION DES DATASETS
# ==========================================
print("\n2.5. Fusion des données tomates et sol...")

# Créer une clé de fusion déterministe (round-robin)
# Chaque ligne tomate reçoit un index de sol en cycle pour maintenir une distribution cohérente
df_tomates['soil_index'] = np.arange(len(df_tomates)) % len(df_soil)
df_soil_indexed = df_soil.reset_index(drop=True).rename(columns={'index': 'soil_index'})

# Fusionner les datasets
df_merged = df_tomates.merge(
    df_soil_indexed,
    left_on='soil_index',
    right_index=True,
    how='left'
)

print(f"   ✓ Dataset fusionné: {len(df_merged)} lignes, {len(df_merged.columns)} colonnes")

print(f"\n📊 COLONNES APRÈS FUSION:")
print(f"   Toutes les colonnes disponibles:")
for i, col in enumerate(df_merged.columns, 1):
    print(f"      {i:2d}. {col:25s} (type: {df_merged[col].dtype}, valeurs uniques: {df_merged[col].nunique()})")

print(f"\n⚠️  VÉRIFICATION DE COMPLÉTUDE:")
for col in df_merged.columns:
    manquantes = df_merged[col].isna().sum()
    if manquantes > 0:
        print(f"   {col}: ⚠️  {manquantes} valeurs manquantes ({100*manquantes/len(df_merged):.1f}%)")
    else:
        print(f"   {col}: ✅ Complète")

# ==========================================
# SÉLECTION DES FEATURES (VARIABLES D'ENTRÉE)
# ==========================================
print("\n3. Sélection des variables d'entraînement...")

feature_columns = [
    'Variete_Encoded',           # Type de tomate
    'Temp_Air_Moy',              # Température de l'air
    'Temp_Sol',                  # Température du sol
    'Humidite_Sol',              # Humidité du sol (%)
    'N', 'P', 'K',               # Nutriments (azote, phosphore, potassium)
    'Prevision_Gelee',           # Présence de gel
    'PH_Level',                  # pH du sol
    'Organic_Matter',            # Matière organique
    'Moisture_Content',          # Teneur en eau
    'Soil_Type_Encoded'          # Type de sol encodé
]

# Vérifier que toutes les colonnes existent
features_disponibles = [col for col in feature_columns if col in df_merged.columns]
features_manquantes = [col for col in feature_columns if col not in df_merged.columns]

if features_manquantes:
    print(f"\n   ⚠️  COLONNES MANQUANTES: {features_manquantes}")
    print(f"   ✅ Colonnes utilisées: {len(features_disponibles)}/{len(feature_columns)}")
else:
    print(f"\n   ✅ Toutes les {len(features_disponibles)} colonnes attendues sont présentes!")

print(f"   🔧 Features utilisées pour l'entraînement:")
for i, f in enumerate(features_disponibles, 1):
    print(f"      {i:2d}. {f}")

# ==========================================
# ANALYSE DE CORRÉLATION
# ==========================================
print("\n4. Analyse de corrélation...")
# Calculer les corrélations avec la cible
correlations = df_merged[features_disponibles + ['Indice_Succes']].corr()['Indice_Succes'].sort_values(ascending=False)

print("\n🔍 CORRÉLATION AVEC L'INDICE DE SUCCÈS (plus proche de ±1 = mieux):")
for feature, corr in correlations.items():
    if feature != 'Indice_Succes':
        force = "✅ FORTE" if abs(corr) > 0.5 else "⚠️  FAIBLE" if abs(corr) > 0.1 else "❌ TRÈS FAIBLE"
        print(f"   {feature:25s} → {corr:7.4f} {force}")

print(f"\n📊 APERÇU DES DONNÉES D'ENTRAÎNEMENT:")
print(df_merged[features_disponibles + ['Indice_Succes']].head(10).to_string())

print("\n3. Sélection optimisée des variables...")

# Prendre uniquement les features avec bonne corrélation (> 0.1)
good_features = correlations[correlations.abs() > 0.05].index.tolist()
good_features = [f for f in good_features if f != 'Indice_Succes']

if len(good_features) < 3:
    print("⚠️  Peu de features corrélées! Utilisation de toutes les features disponibles")
    features_finales = features_disponibles
else:
    print(f"✅ {len(good_features)} features avec corrélation pertinente trouvées")
    features_finales = good_features

print(f"\n   🔧 Features FINALES utilisées pour l'entraînement ({len(features_finales)}):")
for i, f in enumerate(features_finales, 1):
    print(f"      {i:2d}. {f}")

X = df_merged[features_finales].fillna(df_merged[features_finales].mean())
y = df_merged['Indice_Succes']

print(f"\n   📊 Statistiques de la cible (Indice_Succes):")
print(f"      Moyenne: {y.mean():.2f}")
print(f"      Min: {y.min()}, Max: {y.max()}")
print(f"      Écart-type: {y.std():.2f}")

print("\n3.5. Normalisation des features...")
scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)
X = pd.DataFrame(X_scaled, columns=features_finales)
print(f"   ✓ Features normalisées (moyenne=0, écart-type=1)")

print("\n4. Séparation en données d'entraînement (80%) et de test (20%)...")
X_train, X_test, y_train, y_test = train_test_split(
    X, y, 
    test_size=0.2, 
    random_state=42,
    shuffle=True  # Bien mélanger les données
)

print(f"   ✓ Données d'entraînement: {len(X_train)} lignes ({100*len(X_train)/len(X):.1f}%)")
print(f"   ✓ Données de test: {len(X_test)} lignes ({100*len(X_test)/len(X):.1f}%)")
print(f"   ✓ Total utilisé: {len(X)} lignes")

print(f"\n📊 RÉPARTITION:")
print(f"   Train y: min={y_train.min()}, max={y_train.max()}, moyenne={y_train.mean():.2f}")
print(f"   Test y:  min={y_test.min()}, max={y_test.max()}, moyenne={y_test.mean():.2f}")

print("\n5. Entraînement de l'IA Random Forest (modèle SIMPLIFIÉ + régularisé)...")
print("   ⏳ Veuillez patienter...")

# Modèle BEAUCOUP plus simple pour éviter l'overfitting
# - Moins d'arbres (20 au lieu de 100)
# - Profondeur réduite (5 au lieu de 15)  
# - Minimum d'échantillons par split augmenté (20 au lieu de 5)
# - Maximum de features réduit (sqrt) pour la diversité
model = RandomForestRegressor(
    n_estimators=20,           # ⬇️ Réduit (était 100)
    random_state=42,
    n_jobs=2,
    max_depth=5,               # ⬇️ Réduit (était 15)
    min_samples_split=20,      # ⬆️ Augmenté (était 5) - RÉGULARISATION
    min_samples_leaf=10,       # ⬆️ Nouveau - Chaque feuille doit avoir au moins 10 samples
    max_features='sqrt',       # ⬇️ Réduit la variance
    bootstrap=True,
    warm_start=False
)

model.fit(X_train, y_train)
print("   ✅ Entraînement terminé!")

print("\n6. Test de fiabilité sur des données inconnues...")
y_pred_train = model.predict(X_train)
y_pred_test = model.predict(X_test)

# Métriques d'évaluation
mse_test = mean_squared_error(y_test, y_pred_test)
rmse_test = np.sqrt(mse_test)
mae_test = mean_absolute_error(y_test, y_pred_test)
r2_test = r2_score(y_test, y_pred_test)
r2_train = r2_score(y_train, y_pred_train)

print(f"\n✅ FIABILITÉ GLOBALE DE L'IA:")
print(f"   R² Score (Test):  {r2_test:.4f} (0.0 à 1.0, plus proche de 1 = mieux)")
print(f"   R² Score (Train): {r2_train:.4f}")
print(f"   RMSE (Test):      {rmse_test:.2f} points")
print(f"   MAE (Test):       {mae_test:.2f} points")

print(f"\n📊 Rapport détaillé:")
print(f"   Erreur moyenne: ±{mae_test:.1f} points sur l'indice de succès")
print(f"   Le modèle explique {r2_test*100:.1f}% de la variance des données")

# ==========================================
# IMPORTANCE DES VARIABLES
# ==========================================
print("\n7. Analyse de l'importance des variables...")
feature_importance = pd.DataFrame({
    'Feature': features_finales,
    'Importance': model.feature_importances_
}).sort_values('Importance', ascending=False)

print("\n   🔍 Variables les plus influentes:")
for idx, row in feature_importance.head(5).iterrows():
    print(f"      {row['Feature']:25} → {row['Importance']:.4f}")

print("\n8. Sauvegarde du modèle pour l'application finale...")
# Sauvegarder le cerveau (l'IA)
model_path = MODEL_DIR / "modele_potagia.joblib"
joblib.dump(model, model_path)
print(f"   ✓ Modèle sauvegardé: {model_path}")

# Sauvegarder les encodeurs
joblib.dump(le_variete, MODEL_DIR / "encodeur_varietes.joblib")
joblib.dump(le_soil, MODEL_DIR / "encodeur_sols.joblib")
print(f"   ✓ Encodeurs sauvegardés")

# Sauvegarder le scaler
joblib.dump(scaler, MODEL_DIR / "scaler.joblib")
print(f"   ✓ Scaler (normalisation) sauvegardé")

# Sauvegarder la liste des features finales utilisées
joblib.dump(features_finales, MODEL_DIR / "features_list.joblib")
print(f"   ✓ Liste des features sauvegardée")

print("\n" + "="*60)
print("✅ MODÈLE PRÊT POUR LA DÉMONSTRATION TECHNIQUE")
print("="*60)

# ==========================================
# FONCTION DE TEST - SIMULATION UTILISATEUR
# ==========================================

def predire_succes_plantation(variete, temp_air, temp_sol, humidite_sol, 
                             azote_n, phosphore_p, potassium_k, 
                             prevision_gelee, ph_sol, matiere_organique, 
                             humidite_soil, soil_type):
    """
    Fonction de test pour simuler une saisie utilisateur
    Retourne le score prédit par l'IA
    
    Paramètres:
        variete (str): Marmande, Noire de Crimée, Cerise, Cœur de Bœuf
        temp_air (float): Température de l'air en °C
        temp_sol (float): Température du sol en °C
        humidite_sol (int): Humidité du sol en %
        azote_n (int): Niveau d'azote
        phosphore_p (int): Niveau de phosphore
        potassium_k (int): Niveau de potassium
        prevision_gelee (int): 0 ou 1
        ph_sol (float): pH du sol
        matiere_organique (float): % de matière organique
        humidite_soil (int): Humidité du sol (Moisture_Content)
        soil_type (str): Type de sol (Sandy, Loamy, Clayey, Black)
    
    Retour:
        dict: Résultat de la prédiction avec conseil
    """
    
    try:
        # Charger les modèles sauvegardés
        model = joblib.load(MODEL_DIR / "modele_potagia.joblib")
        le_var = joblib.load(MODEL_DIR / "encodeur_varietes.joblib")
        le_sol = joblib.load(MODEL_DIR / "encodeur_sols.joblib")
        features_list = joblib.load(MODEL_DIR / "features_list.joblib")
        scaler_loaded = joblib.load(MODEL_DIR / "scaler.joblib")
        
        # Encoder les variables catégorielles
        variete_encoded = le_var.transform([variete])[0]
        soil_encoded = le_sol.transform([soil_type])[0]
        
        # Créer le vecteur de features
        data_prediction = {
            'Variete_Encoded': variete_encoded,
            'Temp_Air_Moy': temp_air,
            'Temp_Sol': temp_sol,
            'Humidite_Sol': humidite_sol,
            'N': azote_n,
            'P': phosphore_p,
            'K': potassium_k,
            'Prevision_Gelee': prevision_gelee,
            'PH_Level': ph_sol,
            'Organic_Matter': matiere_organique,
            'Moisture_Content': humidite_soil,
            'Soil_Type_Encoded': soil_encoded
        }
        
        # Préparer les données dans l'ordre correct
        X_pred = pd.DataFrame([data_prediction])[features_list]
        
        # Normaliser les données
        X_pred_scaled = scaler_loaded.transform(X_pred)
        
        # Prédiction
        score = float(model.predict(X_pred_scaled)[0])
        score = max(0, min(100, score))  # Clamp entre 0 et 100
        
        # Déterminer le conseil basé sur le score
        if score > 80:
            statut = "✅ EXCELLENT"
            conseil = f"Conditions idéales ! Plantez {variete} maintenant !"
        elif score > 60:
            statut = "✅ BON"
            conseil = f"Bonnes conditions pour planter {variete}."
        elif score > 40:
            statut = "⚠️ MOYEN"
            conseil = f"Conditions acceptables pour {variete}. À surveiller."
        else:
            statut = "❌ MAUVAIS"
            conseil = f"Conditions défavorables. Attendre avant de planter {variete}."
        
        return {
            "score": round(score, 2),
            "statut": statut,
            "conseil": conseil,
            "variete": variete,
            "soil_type": soil_type,
            "succes": True
        }
    
    except Exception as e:
        return {
            "score": 0,
            "statut": "❌ ERREUR",
            "conseil": f"Erreur lors de la prédiction: {str(e)}",
            "succes": False
        }


# ==========================================
# TESTS DE DÉMONSTRATION
# ==========================================

print("\n" + "="*60)
print("🧪 TESTS DE PRÉDICTION - DÉMONSTRATION")
print("="*60)

# Test 1: Marmande avec conditions optimales
print("\n📌 Test 1: Marmande - Conditions optimales")
result1 = predire_succes_plantation(
    variete="Marmande",
    temp_air=25,
    temp_sol=24,
    humidite_sol=70,
    azote_n=110,
    phosphore_p=85,
    potassium_k=160,
    prevision_gelee=0,
    ph_sol=6.8,
    matiere_organique=5.0,
    humidite_soil=70,
    soil_type="Loamy"
)
print(f"   Score: {result1['score']}/100")
print(f"   Statut: {result1['statut']}")
print(f"   Conseil: {result1['conseil']}")

# Test 2: Cerise avec conditions modérées
print("\n📌 Test 2: Cerise - Conditions modérées")
result2 = predire_succes_plantation(
    variete="Cerise",
    temp_air=20,
    temp_sol=19,
    humidite_sol=55,
    azote_n=95,
    phosphore_p=70,
    potassium_k=140,
    prevision_gelee=0,
    ph_sol=6.5,
    matiere_organique=3.5,
    humidite_soil=55,
    soil_type="Sandy"
)
print(f"   Score: {result2['score']}/100")
print(f"   Statut: {result2['statut']}")
print(f"   Conseil: {result2['conseil']}")

# Test 3: Noire de Crimée avec conditions difficiles
print("\n📌 Test 3: Noire de Crimée - Conditions difficiles")
result3 = predire_succes_plantation(
    variete="Noire de Crimée",
    temp_air=12,
    temp_sol=14,
    humidite_sol=35,
    azote_n=80,
    phosphore_p=50,
    potassium_k=120,
    prevision_gelee=1,
    ph_sol=5.5,
    matiere_organique=2.0,
    humidite_soil=35,
    soil_type="Clayey"
)
print(f"   Score: {result3['score']}/100")
print(f"   Statut: {result3['statut']}")
print(f"   Conseil: {result3['conseil']}")

# Test 4: Cœur de Bœuf avec conditions bonnes
print("\n📌 Test 4: Cœur de Bœuf - Conditions bonnes")
result4 = predire_succes_plantation(
    variete="Cœur de Bœuf",
    temp_air=23,
    temp_sol=22,
    humidite_sol=65,
    azote_n=115,
    phosphore_p=80,
    potassium_k=155,
    prevision_gelee=0,
    ph_sol=7.0,
    matiere_organique=4.5,
    humidite_soil=65,
    soil_type="Black"
)
print(f"   Score: {result4['score']}/100")
print(f"   Statut: {result4['statut']}")
print(f"   Conseil: {result4['conseil']}")

print("\n" + "="*60)
print("✅ DÉMONSTRATION TERMINÉE")
print("="*60)

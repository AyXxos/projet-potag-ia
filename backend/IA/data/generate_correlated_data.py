"""
Générateur de données corrélées pour Potag'IA
Génère des données avec des relations causales réalistes ET intègre les données météo
"""

import os
import pandas as pd
import numpy as np
from pathlib import Path
import requests
import json
from dotenv import load_dotenv

np.random.seed(42)

print("🌱 Génération de données CORRÉLÉES avec relations causales...\n")

# ==========================================
# 1. RÉCUPÉRER LES DONNÉES MÉTÉO EN TEMPS RÉEL
# ==========================================

load_dotenv()

API_KEY = os.getenv("OPENWEATHER_API_KEY")
if not API_KEY:
    raise RuntimeError("Missing OPENWEATHER_API_KEY in environment or .env file")
CITY = "Chantepie"
URL = f"https://api.openweathermap.org/data/2.5/weather?q={CITY},FR&APPID={API_KEY}&units=metric"

print("📡 Récupération des données météo en temps réel...")

meteo_live = {}
try:
    response = requests.get(URL, timeout=5)
    response.raise_for_status()
    data = response.json()
    
    meteo_live = {
        "Temp_Air_Moy": data["main"]["temp"],
        "Humidite_Relative": data["main"]["humidity"],
        "Pression": data["main"]["pressure"],
        "Vent_Vitesse": data["wind"]["speed"],
    }
    print(f"   ✅ Données météo récupérées!")
    print(f"      - Température: {meteo_live['Temp_Air_Moy']:.1f}°C")
    print(f"      - Humidité: {meteo_live['Humidite_Relative']}%")
except Exception as e:
    print(f"   ⚠️  Météo non disponible: {e}")
    meteo_live = {
        "Temp_Air_Moy": 23,
        "Humidite_Relative": 65,
        "Pression": 1013,
        "Vent_Vitesse": 3,
    }

# ==========================================
# 2. CONDITIONS OPTIMALES PAR VARIÉTÉ
# ==========================================

varieties = ['Marmande', 'Noire de Crimée', 'Cerise', 'Cœur de Bœuf']
soil_types = ['Sandy', 'Loamy', 'Clayey', 'Black']

optimal_conditions = {
    'Marmande': {'temp_air': 23, 'temp_soil': 22, 'humidity': 65, 'ph': 6.5},
    'Noire de Crimée': {'temp_air': 22, 'temp_soil': 21, 'humidity': 60, 'ph': 6.8},
    'Cerise': {'temp_air': 25, 'temp_soil': 23, 'humidity': 55, 'ph': 6.2},
    'Cœur de Bœuf': {'temp_air': 24, 'temp_soil': 22, 'humidity': 70, 'ph': 6.5}
}

soil_nutrients = {
    'Sandy': {'N': 80, 'P': 60, 'K': 120},
    'Loamy': {'N': 120, 'P': 85, 'K': 140},
    'Clayey': {'N': 100, 'P': 70, 'K': 110},
    'Black': {'N': 150, 'P': 95, 'K': 155}
}

# ==========================================
# 3. GÉNÉRATION DE DONNÉES CORRÉLÉES
# ==========================================

n_samples = 800  # Plus de données pour mieux entraîner

data = []

for i in range(n_samples):
    # Sélectionner variété et type de sol
    variete = np.random.choice(varieties)
    soil_type = np.random.choice(soil_types)
    
    optimal = optimal_conditions[variete]
    
    # GÉNÉRATION CORRÉLÉE :
    # - Température de l'air influe sur température du sol
    # - Humidité influe sur les nutriments disponibles
    # - Type de sol détermine les nutriments de base
    
    # 1. Température de l'air (autour des conditions optimales avec variation saisonnière)
    temp_air = np.random.normal(optimal['temp_air'], 2.5)
    temp_air = np.clip(temp_air, 15, 30)
    
    # 2. Température du sol CORRÉLÉE à temp_air (relation physique réelle)
    soil_temp_deviation = temp_air - optimal['temp_air']
    temp_soil = optimal['temp_soil'] + (soil_temp_deviation * 0.7) + np.random.normal(0, 1.5)
    temp_soil = np.clip(temp_soil, 15, 28)
    
    # 3. Humidité du sol CORRÉLÉE à humidité relative
    base_humidity = optimal['humidity']
    humidity_air = np.random.normal(meteo_live['Humidite_Relative'], 10)
    humidity_air = np.clip(humidity_air, 40, 90)
    
    humidity_soil = base_humidity + (humidity_air - 65) * 0.5 + np.random.normal(0, 5)
    humidity_soil = np.clip(humidity_soil, 30, 90)
    
    # 4. Risque de gel (corrélé avec température basse)
    frost_risk = 1 if temp_air < 18 and np.random.random() < 0.6 else (1 if np.random.random() < 0.15 else 0)
    
    # 5. Nutriments CORRÉLÉS au type de sol
    base_n = soil_nutrients[soil_type]['N']
    base_p = soil_nutrients[soil_type]['P']
    base_k = soil_nutrients[soil_type]['K']
    
    # Les nutriments varient peu mais sont fortement liés au type de sol
    n = np.random.normal(base_n, 8)
    p = np.random.normal(base_p, 6)
    k = np.random.normal(base_k, 10)
    
    # 6. pH du sol (corrélé au type de sol)
    if soil_type == 'Clayey':
        base_ph = 6.2
    elif soil_type == 'Sandy':
        base_ph = 6.4
    elif soil_type == 'Loamy':
        base_ph = 6.7
    else:  # Black
        base_ph = 7.1
    
    ph = np.random.normal(base_ph, 0.3)
    ph = np.clip(ph, 4.5, 8.5)
    
    # 7. Matière organique (corrélée au type de sol)
    if soil_type == 'Black':
        organic_matter = np.random.uniform(4.5, 7.5)
    elif soil_type == 'Loamy':
        organic_matter = np.random.uniform(3.5, 6.5)
    elif soil_type == 'Clayey':
        organic_matter = np.random.uniform(2.5, 5.5)
    else:  # Sandy
        organic_matter = np.random.uniform(1.5, 4.5)
    
    # 8. Humidité du sol (Moisture_Content) - CORRÉLÉE à humidité_sol
    moisture_content = humidity_soil + np.random.normal(0, 3)
    moisture_content = np.clip(moisture_content, 20, 85)
    
    # ==========================================
    # CALCUL DE L'INDICE DE SUCCÈS (relations causales)
    # ==========================================
    
    success = 70  # Score de base
    
    # 1. Température de l'air (optimal ±2°C)
    temp_diff = abs(temp_air - optimal['temp_air'])
    if temp_diff < 2:
        success += 15
    elif temp_diff < 4:
        success += 10
    elif temp_diff < 6:
        success += 5
    else:
        success -= 15
    
    # 2. Température du sol (optimal ±2°C)
    soil_temp_diff = abs(temp_soil - optimal['temp_soil'])
    if soil_temp_diff < 2:
        success += 12
    elif soil_temp_diff < 4:
        success += 8
    else:
        success -= 8
    
    # 3. Humidité du sol (optimal ±5%)
    humidity_diff = abs(humidity_soil - optimal['humidity'])
    if humidity_diff < 5:
        success += 12
    elif humidity_diff < 10:
        success += 8
    elif humidity_diff < 15:
        success += 3
    else:
        success -= 10
    
    # 4. Risque de gel (très négatif)
    if frost_risk == 1:
        success -= 30
    else:
        success += 5
    
    # 5. Nutriments (N, P, K)
    nutrient_score = (n + p + k) / 3
    if nutrient_score > 120:
        success += 12
    elif nutrient_score > 100:
        success += 8
    elif nutrient_score > 80:
        success += 5
    else:
        success -= 5
    
    # 6. pH du sol (optimal ±0.4)
    ph_diff = abs(ph - optimal['ph'])
    if ph_diff < 0.4:
        success += 10
    elif ph_diff < 0.8:
        success += 6
    else:
        success -= 3
    
    # 7. Matière organique (très important)
    if organic_matter > 5:
        success += 10
    elif organic_matter > 3.5:
        success += 6
    elif organic_matter > 2:
        success += 3
    else:
        success -= 5
    
    # 8. Type de sol
    if soil_type == 'Loamy':
        success += 12  # Loamy est le meilleur pour les tomates
    elif soil_type == 'Black':
        success += 8
    elif soil_type == 'Clayey':
        success += 3
    
    # 9. Humidité du sol (Moisture_Content)
    if 45 < moisture_content < 75:
        success += 6
    elif 30 < moisture_content < 85:
        success += 2
    else:
        success -= 8
    
    # Ajouter du bruit réaliste (±8%)
    noise = np.random.normal(0, 4)
    success += noise
    
    # Clipper entre 20 et 100
    success = np.clip(success, 20, 100)
    
    data.append({
        'Variete': variete,
        'Temp_Air_Moy': round(temp_air, 1),
        'Temp_Sol': round(temp_soil, 1),
        'Humidite_Sol': round(humidity_soil, 1),
        'N': round(n, 0),
        'P': round(p, 0),
        'K': round(k, 0),
        'Prevision_Gelee': frost_risk,
        'PH_Level': round(ph, 2),
        'Organic_Matter': round(organic_matter, 2),
        'Moisture_Content': round(moisture_content, 1),
        'Soil_Type': soil_type,
        'Indice_Succes': round(success, 0)
    })

# ==========================================
# CRÉATION ET SAUVEGARDE
# ==========================================

df = pd.DataFrame(data)

output_dir = Path(__file__).parent
BASE_DIR = output_dir.parent

print(f"\n✅ Dataset unifié généré avec succès!")
print(f"   Nombre d'échantillons: {len(df)}")

# Sauvegarder le dataset unifié
df.to_csv(output_dir / "tomates_dataset.csv", index=False)
print(f"\n   ✓ Fichier sauvegardé: tomates_dataset.csv")

# ==========================================
# AFFICHER LES CORRÉLATIONS
# ==========================================

print(f"\n🔍 CORRÉLATIONS AVEC INDICE_SUCCES:")
numeric_cols = df.select_dtypes(include=[np.number]).columns
correlations = df[numeric_cols].corr()['Indice_Succes'].sort_values(ascending=False)

for feature, corr in correlations.items():
    if feature != 'Indice_Succes':
        force = "✅ FORTE" if abs(corr) > 0.6 else "⚠️  BONNE" if abs(corr) > 0.4 else "📊 MODÉRÉE" if abs(corr) > 0.2 else "❌ FAIBLE"
        print(f"   {feature:20} → {corr:7.4f} {force}")

# ==========================================
# STATISTIQUES
# ==========================================

print(f"\n📈 STATISTIQUES DE L'INDICE_SUCCES:")
print(f"   Moyenne: {df['Indice_Succes'].mean():.2f}")
print(f"   Min: {df['Indice_Succes'].min():.0f}, Max: {df['Indice_Succes'].max():.0f}")
print(f"   Écart-type: {df['Indice_Succes'].std():.2f}")

print(f"\n📊 APERÇU DES DONNÉES:")
print(df.head(10).to_string())

print(f"\n💡 PROCHAINES ÉTAPES:")
print(f"   1. ✅ Dataset unifié créé avec corrélations pertinentes")
print(f"   2. Lancer: python train_potagia_ai.py")
print(f"   3. Les données météo en temps réel seront intégrées automatiquement")

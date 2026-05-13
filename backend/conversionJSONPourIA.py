import pandas as pd
import json
import requests
from pathlib import Path

API_KEY = "ca9a3d9e25eaf89e454181917b70ca1e"
CITY = "Chantepie"
URL = f"http://api.openweathermap.org/data/2.5/weather?q={CITY},FR&APPID={API_KEY}&units=metric"

# Chemins des fichiers
BASE_DIR = Path(__file__).parent
DATA_DIR = BASE_DIR / "IA" / "data"
DATA_DIR.mkdir(parents=True, exist_ok=True)

try:
    response = requests.get(URL)
    response.raise_for_status()
    
    data = response.json()
    print(f"✅ Status code: {response.status_code}")
    
    # Données météo propres
    meteo_propre = {
        "Temp_Air_Moy": data["main"]["temp"],
        "Humidite_Relative": data["main"]["humidity"],
        "Pression": data["main"]["pressure"],
        "Vent_Vitesse": data["wind"]["speed"],
        "Vent_Direction": data["wind"].get("deg", 0),
        "Couverture_Nuageuse": data.get("clouds", {}).get("all", 0)
    }
    
    print("\n=== DONNÉES MÉTÉO EN TEMPS RÉEL ===")
    print(json.dumps(meteo_propre, indent=2, ensure_ascii=False))
    
    # ==========================================
    # ENRICHIR AVEC LES DONNÉES DE SOL
    # ==========================================
    print("\n📊 Enrichissement avec les données de sol...")
    
    # Charger les données de sol existantes
    soil_file = DATA_DIR / "soil_quality_dataset.csv"
    if soil_file.exists():
        df_soil = pd.read_csv(soil_file)
        
        # Prendre les moyennes des données de sol
        soil_stats = {
            "PH_Level": df_soil["PH_Level"].mean(),
            "Organic_Matter": df_soil["Organic_Matter"].mean(),
            "Nitrogen_N": df_soil["Nitrogen_N"].mean(),
            "Phosphorus_P": df_soil["Phosphorus_P"].mean(),
            "Potassium_K": df_soil["Potassium_K"].mean(),
            "Moisture_Content": df_soil["Moisture_Content"].mean()
        }
        
        # Combiner météo et sol
        donnees_combinées = {**meteo_propre, **soil_stats}
        
        print("\n✅ Données complètes (Météo + Sol):")
        for key, val in donnees_combinées.items():
            print(f"   {key}: {val:.2f}")
        
        # ==========================================
        # SAUVEGARDER DANS UN CSV POUR L'IA
        # ==========================================
        print("\n💾 Sauvegarde des données pour l'IA...")
        
        # Créer un DataFrame
        df_ia = pd.DataFrame([donnees_combinées])
        
        # Sauvegarder
        meteo_file = DATA_DIR / "donnees_meteo_temps_reel.csv"
        df_ia.to_csv(meteo_file, index=False)
        print(f"   ✓ Données sauvegardées: {meteo_file}")
        
    else:
        print(f"⚠️  Fichier de sol non trouvé: {soil_file}")
    
except requests.exceptions.RequestException as e:
    print(f"❌ Erreur réseau: {e}")
except KeyError as e:
    print(f"❌ Clé manquante: {e}")
except Exception as e:
    print(f"❌ Erreur: {e}")
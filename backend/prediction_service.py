import joblib
import pandas as pd
import random
from pathlib import Path
from datetime import datetime

BASE_DIR = Path(__file__).parent
MODEL_DIR = BASE_DIR / "IA" / "models"

# Cache pour les modèles
_models_cache = {}

def load_artifacts():
    if not _models_cache:
        try:
            _models_cache["model"] = joblib.load(MODEL_DIR / "modele_potagia.joblib")
            _models_cache["le_var"] = joblib.load(MODEL_DIR / "encodeur_varietes.joblib")
            _models_cache["le_sol"] = joblib.load(MODEL_DIR / "encodeur_sols.joblib")
            _models_cache["scaler"] = joblib.load(MODEL_DIR / "scaler.joblib")
            _models_cache["features_list"] = joblib.load(MODEL_DIR / "features_list.joblib")
            _models_cache["perf"] = joblib.load(MODEL_DIR / "performance.joblib")
        except Exception as e:
            print(f"❌ ERREUR CHARGEMENT ARTEFACTS : {e}")
    return _models_cache

def get_prediction(variete: str, meteo: dict, soil_stats: dict, user_overrides: dict = None):
    """
    Interface entre le service météo et le modèle ML Potag'IA.
    Prend en compte les mesures manuelles de l'utilisateur si fournies.
    """
    try:
        # Mois pour la saisonnalité
        date_meteo = meteo.get("date", datetime.now().strftime("%Y-%m-%d"))
        try:
            mois = int(date_meteo.split("-")[1])
        except:
            mois = datetime.now().month

        # Simulation DÉTERMINISTE des données manquantes
        rng = random.Random(variete)
        overrides = user_overrides or {}
        n_sim = overrides.get('n', rng.randint(110, 140))
        p_sim = overrides.get('p', rng.randint(70, 90))
        k_sim = overrides.get('k', rng.randint(130, 160))
        ph_sim = overrides.get('ph', round(rng.uniform(6.2, 6.8), 1))
        om_sim = overrides.get('organic_matter', round(rng.uniform(4.0, 5.5), 1))
        
        temp_air_sim = meteo.get('temp_air', 20)
        temp_sol_sim = meteo.get('temp_sol', 15)
        hum_sim = meteo.get('humidite_sol', 65)
        gel_sim = meteo.get('prevision_gelee', 0)

        # 1. Charger les artefacts (via cache)
        artifacts = load_artifacts()
        if not artifacts:
            # FALLBACK MOCK TOTAL SI PAS DE MODÈLE
            print("⚠️ Modèle non chargé, utilisation d'une simulation heuristique")
            # Score de base selon température et gel
            mock_score = 75.0
            if gel_sim == 1 or temp_air_sim < 5: mock_score = 0
            elif temp_air_sim < 15: mock_score -= 20
            elif temp_air_sim > 30: mock_score -= 15
            
            data_mock = {
                'N': n_sim, 'P': p_sim, 'K': k_sim, 'PH_Level': ph_sim, 
                'Organic_Matter': om_sim, 'Temp_Air_Moy': temp_air_sim, 
                'Temp_Sol': temp_sol_sim, 'Prevision_Gelee': gel_sim,
                'Mois': mois, 'Soil_Type': soil_stats.get("soilType", "Loamy"),
                'is_mock': True
            }
            return max(0, min(100, mock_score)), 80.0, data_mock
            
        model = artifacts["model"]
        le_var = artifacts["le_var"]
        le_sol = artifacts["le_sol"]
        scaler = artifacts["scaler"]
        features_list = artifacts["features_list"]
        perf = artifacts["perf"]
        
        # 2. Encodage Variété avec fallback
        try:
            var_enc = le_var.transform([variete])[0]
            mae_var = perf["variete_mae"].get(variete, perf["global_mae"])
            fiabilite = max(0, round(100 * (1 - mae_var / 50), 1))
        except:
            var_enc = le_var.transform([le_var.classes_[0]])[0]
            fiabilite = 50.0
            
        # 3. Encodage Sol avec fallback
        soil_type = soil_stats.get("soilType", "Loamy")
        try:
            soil_type_enc = le_sol.transform([soil_type])[0]
        except:
            soil_type_enc = le_sol.transform(["Loamy"])[0]

        # 6. Construction du dictionnaire de données
        full_data = {
            'Variete_Encoded': var_enc,
            'Temp_Air_Moy': temp_air_sim,
            'Temp_Sol': temp_sol_sim,
            'Humidite_Sol': hum_sim,
            'N': n_sim, 'P': p_sim, 'K': k_sim,
            'Prevision_Gelee': gel_sim,
            'Mois': mois,
            'PH_Level': ph_sim,
            'Organic_Matter': om_sim,
            'Moisture_Content': hum_sim,
            'Soil_Type_Encoded': soil_type_enc,
            'Diff_Temp': temp_air_sim - temp_sol_sim,
            'Sol_Chaud': 1 if temp_sol_sim > 15 else 0,
            'Gel_Risque': 1 if gel_sim == 1 or temp_air_sim < 5 else 0,
            'Ratio_NP': n_sim / (p_sim + 0.1),
            'Ratio_NK': n_sim / (k_sim + 0.1)
        }
        
        # 7. Préparation finale (filtrage et ordre des colonnes)
        X = pd.DataFrame([full_data])
        
        # S'assurer que TOUTES les colonnes attendues par le scaler/modèle sont là
        for col in features_list:
            if col not in X.columns:
                X[col] = 0
        
        # Filtrer pour ne garder QUE les colonnes du modèle dans le BON ORDRE
        X_final = X[features_list]
        
        # Conversion types NumPy pour data_serializable AVANT le transform potentiellement risqué
        data_serializable = {}
        for k, v in full_data.items():
            if hasattr(v, "item"): 
                data_serializable[k] = v.item()
            else:
                data_serializable[k] = v

        try:
            X_scaled_array = scaler.transform(X_final)
            # Re-créer un DataFrame avec les noms de colonnes pour éviter le UserWarning de sklearn
            X_scaled = pd.DataFrame(X_scaled_array, columns=features_list)
            
            # 8. Prédiction
            score = float(model.predict(X_scaled)[0])
        except Exception as scaler_err:
            print(f"⚠️ Erreur Scaler/Model: {scaler_err}. Fallback Heuristique.")
            # Fallback si le scaler/modèle rejette les colonnes (ex: mismatch version)
            score = 70.0
            if gel_sim == 1: score = 0
            data_serializable['error_detail'] = str(scaler_err)
        
        # Règle de sécurité finale
        if meteo.get('prevision_gelee') == 1: 
            score = 0
            
        return max(0, min(100, score)), fiabilite, data_serializable

    except Exception as e:
        import traceback
        print(f"❌ ERREUR CRITIQUE INFÉRENCE : {str(e)}")
        traceback.print_exc()
        return 0, 0, {"error": str(e)}

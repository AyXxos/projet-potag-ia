import joblib
import pandas as pd
import random
from pathlib import Path
from datetime import datetime

BASE_DIR = Path(__file__).parent
MODEL_DIR = BASE_DIR / "IA" / "models"

def get_prediction(variete: str, meteo: dict, soil_stats: dict, user_overrides: dict = None):
    """
    Interface entre le service météo et le modèle ML Potag'IA.
    Prend en compte les mesures manuelles de l'utilisateur si fournies.
    """
    try:
        # 1. Charger les artefacts
        model = joblib.load(MODEL_DIR / "modele_potagia.joblib")
        le_var = joblib.load(MODEL_DIR / "encodeur_varietes.joblib")
        le_sol = joblib.load(MODEL_DIR / "encodeur_sols.joblib")
        scaler = joblib.load(MODEL_DIR / "scaler.joblib")
        features_list = joblib.load(MODEL_DIR / "features_list.joblib")
        perf = joblib.load(MODEL_DIR / "performance.joblib")
        
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
        
        # 4. Extraction du mois (Saisonnalité)
        date_meteo = meteo.get("date", datetime.now().strftime("%Y-%m-%d"))
        try:
            # Format attendu : YYYY-MM-DD
            mois = int(date_meteo.split("-")[1])
        except:
            mois = datetime.now().month

        # 5. Gestion des overrides et simulation V0
        overrides = user_overrides or {}
        
        # Simulation sol de qualité (V0)
        n_sim = overrides.get('n', random.randint(110, 140))
        p_sim = overrides.get('p', random.randint(70, 90))
        k_sim = overrides.get('k', random.randint(130, 160))
        ph_sim = overrides.get('ph', round(random.uniform(6.2, 6.8), 1))
        om_sim = overrides.get('organic_matter', round(random.uniform(4.0, 5.5), 1))

        # Ajustement météo démo
        temp_air_sim = meteo.get('temp_air', 20)
        if temp_air_sim < 15: temp_air_sim = random.randint(18, 24)
        
        temp_sol_sim = meteo.get('temp_sol', 15)
        if temp_sol_sim < 12: temp_sol_sim = random.randint(14, 18)

        # 6. Construction du dictionnaire de données
        full_data = {
            'Variete_Encoded': var_enc,
            'Temp_Air_Moy': temp_air_sim,
            'Temp_Sol': temp_sol_sim,
            'Humidite_Sol': meteo.get('humidite_sol', 65),
            'N': n_sim, 'P': p_sim, 'K': k_sim,
            'Prevision_Gelee': 0, # Forcé à 0 pour démo V0
            'Mois': mois,
            'PH_Level': ph_sim,
            'Organic_Matter': om_sim,
            'Moisture_Content': meteo.get('humidite_sol', 65),
            'Soil_Type_Encoded': soil_type_enc,
            'Diff_Temp': temp_air_sim - temp_sol_sim,
            'Sol_Chaud': 1,
            'Gel_Risque': 0,
            'Ratio_NP': n_sim / (p_sim + 0.1),
            'Ratio_NK': n_sim / (k_sim + 0.1)
        }
        
        # 7. Préparation finale (filtrage et ordre des colonnes)
        X = pd.DataFrame([full_data])
        # S'assurer que TOUTES les features attendues sont présentes
        for col in features_list:
            if col not in X.columns:
                X[col] = 0
        
        X_final = X[features_list]
        X_scaled = scaler.transform(X_final)
        
        # 8. Prédiction
        score = float(model.predict(X_final_scaled)[0]) if 'X_final_scaled' in locals() else float(model.predict(X_scaled)[0])
        
        # Règle de sécurité finale
        if meteo.get('prevision_gelee') == 1: 
            score = 0
            
        # --- CORRECTION SÉRIALISATION JSON ---
        # Convertir les types NumPy (int64, float64) en types Python natifs (int, float)
        # pour éviter l'erreur PydanticSerializationError
        data_serializable = {}
        for k, v in full_data.items():
            if hasattr(v, "item"): # Est-ce un type NumPy ?
                data_serializable[k] = v.item()
            else:
                data_serializable[k] = v

        return max(0, min(100, score)), fiabilite, data_serializable

    except Exception as e:
        import traceback
        print(f"❌ ERREUR INFÉRENCE : {str(e)}")
        traceback.print_exc()
        return 0, 0, {}

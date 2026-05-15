# GEMINI.md

Context for Gemini when working on Potag'IA AI development.

## Project summary
- Potag'IA is an Expo/React Native app with a FastAPI backend.
- AI training script: backend/IA/train_potagia_ai.py
- Data: backend/IA/data/*.csv
- Saved artifacts: backend/IA/models/*.joblib

## AI goal
Predict "Indice_Succes" (0-100) for tomato planting based on weather, soil, nutrients, and variety.

## Dataset expectations
- tomates_dataset.csv columns: Variete, Temp_Air_Moy, Temp_Sol, Humidite_Sol, N, P, K, Prevision_Gelee, Indice_Succes
- soil_quality_dataset.csv columns: Soil_Type, PH_Level, Organic_Matter, Moisture_Content
- Optional: donnees_meteo_temps_reel.csv

## Training pipeline (current)
1. Load datasets.
2. Label encode Variete and Soil_Type.
3. Merge tomatoes + soil by round-robin (soil_index).
4. Select features, filter by correlation > 0.05.
5. Fill missing numeric values with mean.
6. Standardize features (StandardScaler).
7. Train/test split 80/20.
8. Train RandomForestRegressor with regularized hyperparams.
9. Save model + encoders + scaler + features list to models/.

## Inference contract
- predire_succes_plantation(...) loads artifacts and expects features in features_list.joblib order.
- Keep artifact names stable:
  - modele_potagia.joblib
  - encodeur_varietes.joblib
  - encodeur_sols.joblib
  - scaler.joblib
  - features_list.joblib

## Working guidelines
- Prefer small, focused changes; keep console diagnostics unless asked to remove.
- If you change the feature set or encoders, update both training and inference paths.
- Avoid breaking the feature order contract; always save features_list.joblib.
- If you add dependencies, update backend/requirements.txt.

## How to run
From backend:
- python -m venv venv
- .\venv\Scripts\activate
- pip install -r requirements.txt
- python IA/train_potagia_ai.py

## Ask before big changes
- Target metric or accuracy goal?
- Acceptable training time and model size?
- Any new data sources or schema changes?

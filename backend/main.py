from fastapi import FastAPI, Depends, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from datetime import datetime, date
import models
import schemas
from database import engine, get_db
import weather_service
import prediction_service
import json

# Create database tables
models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="E-Potager API")

# Middleware pour logger les réponses dans la console
@app.middleware("http")
async def log_responses(request: Request, call_next):
    start_time = datetime.now()
    response = await call_next(request)
    duration = (datetime.now() - start_time).total_seconds() * 1000
    
    print(f"\n--- {request.method} {request.url.path} ---")
    print(f"Status: {response.status_code} | Duration: {duration:.2f}ms")
    
    # On ne logue le corps que pour les routes AI ou si c'est court
    # Note: Accéder au corps ici est complexe avec FastAPI (StreamingResponse),
    # donc on va plutôt logger directement dans les endpoints pour le contenu.
    return response

# Setup CORS to allow your React frontend to communicate with the API
origins = [
    "http://localhost:5173", # Vite default port
    "http://127.0.0.1:5173",
    "http://localhost:19006", # Expo Web
    "*" # Pour le dev mobile
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {"message": "Bienvenue sur l'API E-Potager"}

@app.post("/ai/predict", response_model=schemas.PredictionResponse)
def predict_plantation_ai(req: schemas.PredictionRequest, db: Session = Depends(get_db)):
    # 1. Météo (avec fallback mock intégré au service)
    forecast = weather_service.get_weather_forecast(req.lat, req.lon, days=1)
    meteo = forecast[0] if forecast else {
        "date": datetime.now().strftime("%Y-%m-%d"),
        "temp_air": 20, "temp_sol": 15, "humidite_sol": 60, "prevision_gelee": 0
    }
    
    # 2. Données Sol (réelles ou fictives)
    garden_stats = db.query(models.GardenStats).first()
    if not garden_stats:
        print("ℹ️ GardenStats vides -> Utilisation de données de sol fictives")
        soil_data = {"soilType": "Loamy"}
    else:
        soil_data = {"soilType": garden_stats.soilType}
    
    # 3. Overrides utilisateur
    user_overrides = {k: v for k, v in {
        'n': req.n, 'p': req.p, 'k': req.k,
        'ph': req.ph, 'organic_matter': req.organic_matter
    }.items() if v is not None}
    
    # 4. Prédiction (avec simulation des valeurs manquantes et fallback mock total)
    score, fiabilite, data_used = prediction_service.get_prediction(
        req.variete, meteo, soil_data, user_overrides
    )
    
    # 5. Recommandation
    from IA.train_potagia_ai import obtenir_recommandation
    statut, conseil = obtenir_recommandation(score, meteo["prevision_gelee"])
    
    res = {
        "score": round(score, 2), 
        "fiabilite": fiabilite, 
        "statut": statut, 
        "conseil": conseil, 
        "meteo": meteo, 
        "data_used": data_used
    }
    print(f"✅ AI Predict (MOCK={data_used.get('is_mock', False)}) for {req.variete}")
    return res

@app.post("/ai/best-planting-date", response_model=schemas.BestDateResponse)
def get_best_planting_date(req: schemas.PredictionRequest, db: Session = Depends(get_db)):
    # 1. Prévisions sur 60 jours (avec fallback mock intégré au service)
    forecast = weather_service.get_weather_forecast(req.lat, req.lon, days=60)
    
    # 2. Stats sol
    garden_stats = db.query(models.GardenStats).first()
    soil_data = {"soilType": garden_stats.soilType if garden_stats else "Loamy"}
    user_overrides = {k: v for k, v in {
        'n': req.n, 'p': req.p, 'k': req.k, 
        'ph': req.ph, 'organic_matter': req.organic_matter
    }.items() if v is not None}

    # 3. Calculer les scores pour chaque jour
    daily_results = []
    for day_meteo in forecast:
        score, fiabilite, _ = prediction_service.get_prediction(
            req.variete, day_meteo, soil_data, user_overrides
        )
        daily_results.append({
            "date": day_meteo["date"],
            "score": round(score, 2),
            "prevision_gelee": day_meteo["prevision_gelee"]
        })
    
    # 4. Trier par score décroissant
    sorted_days = sorted(daily_results, key=lambda x: (x["score"], -datetime.strptime(x["date"], "%Y-%m-%d").timestamp()), reverse=True)
    
    # 5. Meilleur résultat
    best_result = sorted_days[0]
    top_5 = sorted_days[:5]
    
    # 6. Formater recommandation finale
    from IA.train_potagia_ai import obtenir_recommandation
    statut, conseil = obtenir_recommandation(best_result["score"], best_result["prevision_gelee"])
    
    res = {
        "best_date": best_result["date"],
        "best_score": best_result["score"],
        "statut": statut,
        "conseil": conseil,
        "daily_scores": daily_results,
        "top_5_days": top_5
    }
    return res

@app.post("/api/predict-plantation", response_model=schemas.PredictionResponse)
def predict_plantation(req: schemas.PredictionRequest, db: Session = Depends(get_db)):
    return predict_plantation_ai(req, db)

# --- GARDEN STATS ---
@app.get("/api/garden-stats", response_model=schemas.GardenStats)
def get_garden_stats(db: Session = Depends(get_db)):
    stats = db.query(models.GardenStats).first()
    if not stats:
        raise HTTPException(status_code=404, detail="Stats non trouvées")
    return stats

# --- CURRENT VEGETABLES ---
@app.get("/api/current-vegetables", response_model=list[schemas.CurrentVegetable])
def get_current_vegetables(db: Session = Depends(get_db)):
    return db.query(models.CurrentVegetable).all()

# --- LIBRARY ---
@app.get("/api/library", response_model=list[schemas.LibraryItem])
def get_library(db: Session = Depends(get_db)):
    return db.query(models.LibraryItem).all()

# --- SEED ROUTE ---
@app.post("/api/seed")
def seed_database(db: Session = Depends(get_db)):
    from datetime import datetime, date, timedelta
    import models

    db.query(models.GardenStats).delete()
    db.query(models.CurrentVegetable).delete()
    db.query(models.LibraryItem).delete()

    garden_stats = [models.GardenStats(solHealth=90, humidity=30, temperature=20, soilType="Loamy", totalSize="50 m²")]
    
    current_vegetables = [
        models.CurrentVegetable(name="Marmande", status="Sprout"),
        models.CurrentVegetable(name="Cerise", status="Leaf"),
    ]

    library_seed = [
        {"name": "Marmande", "season": "Printemps", "tips": "Tuteurez tôt."},
        {"name": "Cerise", "season": "Printemps", "tips": "Productive."},
    ]

    library_items = []
    for item in library_seed:
        library_items.append(models.LibraryItem(
            name=item["name"],
            season=item["season"], tips=item["tips"]))

    db.add_all(garden_stats + current_vegetables + library_items)
    db.commit()
    return {"message": "Base de données initialisée !"}

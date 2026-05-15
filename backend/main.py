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
    # ... (code existant)
    forecast = weather_service.get_weather_forecast(req.lat, req.lon, days=1)
    if not forecast:
        raise HTTPException(status_code=503, detail="Service météo indisponible")
    meteo = forecast[0]
    
    garden_stats = db.query(models.GardenStats).first()
    soil_data = {"soilType": garden_stats.soilType if garden_stats else "Loamy"}
    
    user_overrides = {k: v for k, v in {
        'n': req.n, 'p': req.p, 'k': req.k,
        'ph': req.ph, 'organic_matter': req.organic_matter
    }.items() if v is not None}
    
    score, fiabilite, data_used = prediction_service.get_prediction(
        req.variete, meteo, soil_data, user_overrides
    )
    
    from IA.train_potagia_ai import obtenir_recommandation
    statut, conseil = obtenir_recommandation(score, meteo["prevision_gelee"])
    
    res = {
        "score": round(score, 2), "fiabilite": fiabilite, "statut": statut, "conseil": conseil, "meteo": meteo, "data_used": data_used
    }
    print(f"Response AI Predict: {json.dumps(res, indent=2)}")
    return res

@app.post("/ai/best-planting-date", response_model=schemas.BestDateResponse)
def get_best_planting_date(req: schemas.PredictionRequest, db: Session = Depends(get_db)):
    # 1. Prévisions sur 60 jours
    forecast = weather_service.get_weather_forecast(req.lat, req.lon, days=60)
    if not forecast:
        raise HTTPException(status_code=503, detail="Prévisions indisponibles")
    
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
    
    # 4. Trier par score décroissant, puis par date croissante (priorité au plus tôt si score égal)
    # On ajoute une petite pénalité de 0.01 par jour pour favoriser légèrement les dates proches à score égal
    sorted_days = sorted(daily_results, key=lambda x: (x["score"], -datetime.strptime(x["date"], "%Y-%m-%d").timestamp()), reverse=True)
    
    # 5. Meilleur résultat (le premier après tri)
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
    # Log simplifié pour la console (on ne logue pas les 60 jours de daily_scores pour rester lisible)
    log_res = {k: v for k, v in res.items() if k != "daily_scores"}
    print(f"Response Best Planting Date: {json.dumps(log_res, indent=2)}")
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

# --- TO PLANT ---
@app.get("/api/to-plant", response_model=list[schemas.ToPlant])
def get_to_plant_list(db: Session = Depends(get_db)):
    return db.query(models.ToPlant).all()

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
    db.query(models.ToPlant).delete()
    db.query(models.LibraryItem).delete()

    garden_stats = [models.GardenStats(solHealth=90, humidity=30, temperature=20, soilType="Loamy", totalSize="50 m²")]
    
    current_vegetables = [
        models.CurrentVegetable(name="Marmande", status="Sprout", plantedDate=date(2026, 3, 20), icon="Sprout"),
        models.CurrentVegetable(name="Cerise", status="Leaf", plantedDate=date(2026, 3, 15), icon="Leaf"),
    ]

    to_plant = [
        models.ToPlant(name="Marmande", urgency="Haute"),
        models.ToPlant(name="Cerise", urgency="Moyenne"),
    ]

    library_seed = [
        {"name": "Marmande", "period": "75 jours", "season": "Printemps", "waterNeeds": "Élevées", "tips": "Tuteurez tôt."},
        {"name": "Cerise", "period": "60 jours", "season": "Printemps", "waterNeeds": "Moyennes", "tips": "Productive."},
    ]

    library_items = []
    for item in library_seed:
        library_items.append(models.LibraryItem(
            name=item["name"], period=item["period"], plantingStart=date(2026, 5, 1), 
            plantingEnd=date(2026, 5, 30), plantingDate=date(2026, 5, 15), 
            season=item["season"], waterNeeds=item["waterNeeds"], tips=item["tips"]))

    db.add_all(garden_stats + current_vegetables + to_plant + library_items)
    db.commit()
    return {"message": "Base de données initialisée !"}

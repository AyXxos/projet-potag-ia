from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from datetime import date
import models
import schemas
from database import engine, get_db

# Create database tables
models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="E-Potager API")

# Setup CORS to allow your React frontend to communicate with the API
origins = [
    "http://localhost:5173", # Vite default port
    "http://127.0.0.1:5173"
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

# --- SEED ROUTE (Pour initialiser facilement la BDD) ---
@app.post("/api/seed")
def seed_database(db: Session = Depends(get_db)):
    from datetime import datetime, date, timedelta
    import models

    # Effacer les données existantes
    db.query(models.GardenStats).delete()
    db.query(models.CurrentVegetable).delete()
    db.query(models.ToPlant).delete()
    db.query(models.LibraryItem).delete()

    # GardenStats - Conditions idéales pour la culture des tomates en printemps (mai 2026, France)
    garden_stats = [
        models.GardenStats(
            solHealth=90,
            humidity=30,
            temperature=20,
            soilType="Terre naturelle",
            totalSize="50 m²"
        )
    ]

    # CurrentVegetable - Variétés de tomates actuellement en terre (plantées entre mars et avril 2026)
    current_vegetables = [
        models.CurrentVegetable(name="Tomate Cerise Sweet Million", status="Sprout", plantedDate=datetime(2026, 3, 20), icon="Sprout"),
        models.CurrentVegetable(name="Tomate Cœur de Bœuf", status="Leaf", plantedDate=datetime(2026, 3, 15), icon="Leaf"),
        models.CurrentVegetable(name="Tomate Noire de Crimée", status="Sprout", plantedDate=datetime(2026, 4, 1), icon="Sprout"),
        models.CurrentVegetable(name="Tomate San Marzano", status="Leaf", plantedDate=datetime(2026, 3, 18), icon="Leaf"),
    ]

    # ToPlant - Variétés de tomates à semer ou planter en mai 2026
    to_plant = [
        models.ToPlant(name="Tomate Cerise Sweet Million", urgency="Haute"),
        models.ToPlant(name="Tomate Cœur de Bœuf", urgency="Moyenne"),
        models.ToPlant(name="Tomate Noire de Crimée", urgency="Haute"),
        models.ToPlant(name="Tomate San Marzano", urgency="Moyenne"),
    ]

    # LibraryItem - 4 variétés de tomates avec conseils experts
    base_start = date(2026, 5, 11)
    offsets = [0, 7, 14, 21]
    library_seed = [
        {
            "name": "Tomate Cerise Sweet Million",
            "period": "60-70 jours",
            "season": "Printemps-Été",
            "waterNeeds": "Élevées",
            "tips": "Variété très productive. Tuteurez dès la plantation. Pincez les gourmands régulièrement. Arrosage au pied pour éviter le mildiou."
        },
        {
            "name": "Tomate Cœur de Bœuf",
            "period": "80-90 jours",
            "season": "Printemps-Été",
            "waterNeeds": "Élevées",
            "tips": "Plantez en poquet de 2-3 pieds. Supprimez les feuilles basses pour aérer la base. Récoltez quand le fruit est bien rouge et légèrement mou."
        },
        {
            "name": "Tomate Noire de Crimée",
            "period": "75-85 jours",
            "season": "Printemps-Été",
            "waterNeeds": "Modérées",
            "tips": "Variété résistante à la sécheresse. Semis en intérieur 8 semaines avant les dernières gelées. Espacement de 50 cm entre les plants."
        },
        {
            "name": "Tomate San Marzano",
            "period": "80-90 jours",
            "season": "Printemps-Été",
            "waterNeeds": "Élevées",
            "tips": "Tomate italienne idéale pour les coulis. Plantez en lignes espacées de 60 cm. Tuteurez et pincez les gourmands."
        }
    ]

    library_items = []
    for item, offset in zip(library_seed, offsets):
        start = base_start + timedelta(days=offset)
        end = start + timedelta(days=6)
        exact = start + timedelta(days=2)
        library_items.append(
            models.LibraryItem(
                name=item["name"],
                period=item["period"],
                plantingStart=start,
                plantingEnd=end,
                plantingDate=exact,
                season=item["season"],
                waterNeeds=item["waterNeeds"],
                tips=item["tips"]
            )
        )

    # Ajout de toutes les données à la session
    db.add_all(garden_stats + current_vegetables + to_plant + library_items)
    db.commit()
    return {"message": "Base de données initialisée avec succès avec le dataset Mistral !"}

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
    from datetime import datetime
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
            humidity=70,
            temperature=20,
            soilType="Drainant et riche en compost",
            totalSize="50 m²"
        )
    ]

    # CurrentVegetable - Variétés de tomates actuellement en terre (plantées entre mars et avril 2026)
    current_vegetables = [
        models.CurrentVegetable(name="Tomate Cerise Sweet Million", status="Sprout", plantedDate=datetime(2026, 3, 20), icon="Sprout"),
        models.CurrentVegetable(name="Tomate Cœur de Bœuf", status="Leaf", plantedDate=datetime(2026, 3, 15), icon="Leaf"),
        models.CurrentVegetable(name="Tomate Noire de Crimée", status="Sprout", plantedDate=datetime(2026, 4, 1), icon="Sprout"),
        models.CurrentVegetable(name="Tomate Saint-Pierre", status="Leaf", plantedDate=datetime(2026, 3, 25), icon="Leaf"),
        models.CurrentVegetable(name="Tomate Andine Cornue", status="Sprout", plantedDate=datetime(2026, 4, 5), icon="Sprout"),
        models.CurrentVegetable(name="Tomate Ananas", status="Leaf", plantedDate=datetime(2026, 3, 10), icon="Leaf"),
        models.CurrentVegetable(name="Tomate Green Zebra", status="Sprout", plantedDate=datetime(2026, 4, 10), icon="Sprout"),
        models.CurrentVegetable(name="Tomate San Marzano", status="Leaf", plantedDate=datetime(2026, 3, 18), icon="Leaf"),
        models.CurrentVegetable(name="Tomate Brandywine", status="Sprout", plantedDate=datetime(2026, 4, 2), icon="Sprout"),
        models.CurrentVegetable(name="Tomate Yellow Pear", status="Leaf", plantedDate=datetime(2026, 3, 30), icon="Leaf"),
    ]

    # ToPlant - Variétés de tomates à semer ou planter en mai 2026
    to_plant = [
        models.ToPlant(name="Tomate Black Cherry", urgency="Haute"),
        models.ToPlant(name="Tomate Blue Berries", urgency="Haute"),
        models.ToPlant(name="Tomate White Queen", urgency="Moyenne"),
        models.ToPlant(name="Tomate Purple Calabash", urgency="Moyenne"),
        models.ToPlant(name="Tomate Gold Medal", urgency="Basse"),
        models.ToPlant(name="Tomate Hillbilly Potato Leaf", urgency="Basse"),
        models.ToPlant(name="Tomate Cherokee Purple", urgency="Haute"),
        models.ToPlant(name="Tomate Sungold", urgency="Moyenne"),
    ]

    # LibraryItem - 20+ variétés de tomates avec conseils experts
    library_items = [
        models.LibraryItem(
            name="Tomate Cerise Sweet Million",
            period="60-70 jours",
            season="Printemps-Été",
            waterNeeds="Élevées",
            tips="Variété très productive. Tuteurez dès la plantation. Pincez les gourmands régulièrement. Arrosage au pied pour éviter le mildiou."
        ),
        models.LibraryItem(
            name="Tomate Cœur de Bœuf",
            period="80-90 jours",
            season="Printemps-Été",
            waterNeeds="Élevées",
            tips="Plantez en poquet de 2-3 pieds. Supprimez les feuilles basses pour aérer la base. Récoltez quand le fruit est bien rouge et légèrement mou."
        ),
        models.LibraryItem(
            name="Tomate Noire de Crimée",
            period="75-85 jours",
            season="Printemps-Été",
            waterNeeds="Modérées",
            tips="Variété résistante à la sécheresse. Semis en intérieur 8 semaines avant les dernières gelées. Espacement de 50 cm entre les plants."
        ),
        models.LibraryItem(
            name="Tomate Saint-Pierre",
            period="70-80 jours",
            season="Printemps-Été",
            waterNeeds="Élevées",
            tips="Idéale pour les climats frais. Associez avec des œillets d'Inde pour éloigner les nématodes. Paillage recommandé."
        ),
        models.LibraryItem(
            name="Tomate Andine Cornue",
            period="80-90 jours",
            season="Printemps-Été",
            waterNeeds="Élevées",
            tips="Forme allongée, parfaite pour les sauces. Tuteurez solidement. Évitez l'excès d'eau en fin de culture pour concentrer les saveurs."
        ),
        models.LibraryItem(
            name="Tomate Ananas",
            period="85-95 jours",
            season="Printemps-Été",
            waterNeeds="Élevées",
            tips="Fruits jaunes striés de rouge, très sucrés. Plantez en plein soleil. Récoltez à maturité complète pour un goût optimal."
        ),
        models.LibraryItem(
            name="Tomate Green Zebra",
            period="75-85 jours",
            season="Printemps-Été",
            waterNeeds="Modérées",
            tips="Variété originale à rayures vertes et jaunes. Goût acidulé. Supporte bien la chaleur. Arrosage régulier mais sans excès."
        ),
        models.LibraryItem(
            name="Tomate San Marzano",
            period="80-90 jours",
            season="Printemps-Été",
            waterNeeds="Élevées",
            tips="Tomate italienne idéale pour les coulis. Plantez en lignes espacées de 60 cm. Tuteurez et pincez les gourmands."
        ),
        models.LibraryItem(
            name="Tomate Brandywine",
            period="85-100 jours",
            season="Printemps-Été",
            waterNeeds="Élevées",
            tips="Variété ancienne à feuilles de pomme de terre. Goût exceptionnel. Sensible au mildiou : traitez préventivement au purin de prêle."
        ),
        models.LibraryItem(
            name="Tomate Yellow Pear",
            period="70-80 jours",
            season="Printemps-Été",
            waterNeeds="Modérées",
            tips="Petits fruits jaunes en forme de poire. Très productive. Parfaite pour les salades. Résiste bien aux maladies."
        ),
        models.LibraryItem(
            name="Tomate Black Cherry",
            period="65-75 jours",
            season="Printemps-Été",
            waterNeeds="Élevées",
            tips="Tomates cerises noires, très sucrées. Plantez en pot ou en pleine terre. Arrosage quotidien en période de sécheresse."
        ),
        models.LibraryItem(
            name="Tomate Blue Berries",
            period="70-80 jours",
            season="Printemps-Été",
            waterNeeds="Modérées",
            tips="Petits fruits bleus à maturité. Variété résistante au froid. Idéale pour les climats tempérés. Goût fruité et légèrement acidulé."
        ),
        models.LibraryItem(
            name="Tomate White Queen",
            period="80-90 jours",
            season="Printemps-Été",
            waterNeeds="Modérées",
            tips="Tomates blanches, douces et peu acides. Parfaite pour les enfants. Plantez en situation ensoleillée mais à l'abri du vent."
        ),
        models.LibraryItem(
            name="Tomate Purple Calabash",
            period="85-95 jours",
            season="Printemps-Été",
            waterNeeds="Élevées",
            tips="Fruits violets et côtelés. Variété rare, saveur riche et complexe. Tuteurez et pincez pour favoriser la ramification."
        ),
        models.LibraryItem(
            name="Tomate Gold Medal",
            period="80-90 jours",
            season="Printemps-Été",
            waterNeeds="Modérées",
            tips="Gros fruits roses, très charnus. Variété ancienne américaine. Espacement de 70 cm entre les plants. Récoltez avant pleine maturité pour éviter les fentes."
        ),
        models.LibraryItem(
            name="Tomate Hillbilly Potato Leaf",
            period="90-100 jours",
            season="Printemps-Été",
            waterNeeds="Élevées",
            tips="Feuillage de type pomme de terre. Fruits jaunes rayés de rouge, très gros. Sensible aux maladies : surveillez l'humidité."
        ),
        models.LibraryItem(
            name="Tomate Cherokee Purple",
            period="80-90 jours",
            season="Printemps-Été",
            waterNeeds="Élevées",
            tips="Variété héritage, très populaire aux États-Unis. Goût riche et sucré. Plantez en sol profond et bien drainé."
        ),
        models.LibraryItem(
            name="Tomate Sungold",
            period="55-65 jours",
            season="Printemps-Été",
            waterNeeds="Élevées",
            tips="Tomate cerise orange, très sucrée. Variété précoce et productive. Arrosage régulier pour éviter le stress hydrique."
        ),
        models.LibraryItem(
            name="Tomate Black Krim",
            period="70-80 jours",
            season="Printemps-Été",
            waterNeeds="Modérées",
            tips="Originaire de Crimée, fruits noirs-rouges. Goût salé et complexe. Résiste bien à la sécheresse une fois installée."
        ),
        models.LibraryItem(
            name="Tomate Yellow Brandywine",
            period="85-95 jours",
            season="Printemps-Été",
            waterNeeds="Élevées",
            tips="Variante jaune de la Brandywine. Fruits très gros et peu acides. Tuteurez solidement. Évitez les sols trop humides."
        ),
    ]

    # Ajout de toutes les données à la session
    db.add_all(garden_stats + current_vegetables + to_plant + library_items)
    db.commit()
    return {"message": "Base de données initialisée avec succès avec le dataset Mistral !"}

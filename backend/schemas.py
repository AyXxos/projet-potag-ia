from pydantic import BaseModel
from datetime import date

class GardenStatsBase(BaseModel):
    solHealth: int
    humidity: int
    temperature: int
    soilType: str
    totalSize: str

class GardenStats(GardenStatsBase):
    id: int
    class Config:
        from_attributes = True

class CurrentVegetableBase(BaseModel):
    name: str
    status: str

class CurrentVegetable(CurrentVegetableBase):
    id: int
    class Config:
        from_attributes = True

class LibraryItemBase(BaseModel):
    name: str
    season: str
    tips: str

class LibraryItem(LibraryItemBase):
    id: int
    class Config:
        from_attributes = True

class PredictionRequest(BaseModel):
    user_id: int | None = None
    variete: str
    lat: float
    lon: float
    # Paramètres optionnels (si l'utilisateur a des capteurs)
    n: int | None = None
    p: int | None = None
    k: int | None = None
    ph: float | None = None
    organic_matter: float | None = None

class PredictionResponse(BaseModel):
    score: float
    fiabilite: float
    statut: str
    conseil: str
    meteo: dict
    data_used: dict # Pour transparence sur les valeurs utilisées (réelles vs défaut)

class BestDateResponse(BaseModel):
    best_date: str
    best_score: float
    statut: str
    conseil: str
    daily_scores: list[dict]
    top_5_days: list[dict]

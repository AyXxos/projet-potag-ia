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
    plantedDate: date
    icon: str

class CurrentVegetable(CurrentVegetableBase):
    id: int
    class Config:
        from_attributes = True

class ToPlantBase(BaseModel):
    name: str
    urgency: str

class ToPlant(ToPlantBase):
    id: int
    class Config:
        from_attributes = True

class LibraryItemBase(BaseModel):
    name: str
    period: str
    plantingStart: date
    plantingEnd: date
    plantingDate: date
    season: str
    waterNeeds: str
    tips: str

class LibraryItem(LibraryItemBase):
    id: int
    class Config:
        from_attributes = True

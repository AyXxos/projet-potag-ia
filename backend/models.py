from sqlalchemy import Column, Integer, String, Date
from database import Base

class GardenStats(Base):
    __tablename__ = "garden_stats"

    id = Column(Integer, primary_key=True, index=True)
    solHealth = Column(Integer)
    humidity = Column(Integer)
    temperature = Column(Integer)
    soilType = Column(String)
    totalSize = Column(String)

class CurrentVegetable(Base):
    __tablename__ = "current_vegetables"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    status = Column(String)
    plantedDate = Column(Date)
    icon = Column(String)

class ToPlant(Base):
    __tablename__ = "to_plant"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    urgency = Column(String)

class LibraryItem(Base):
    __tablename__ = "library"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    period = Column(String)
    season = Column(String)
    waterNeeds = Column(String)
    tips = Column(String)

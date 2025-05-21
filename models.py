
# models.py
from sqlalchemy import DateTime, Enum, String, Column, Integer, Float, ForeignKey, Table, Boolean, Date
from sqlalchemy.orm import relationship, declarative_base
from datetime import datetime

from sqlalchemy.sql import func
Base = declarative_base()

# Table d'association pour la relation many-to-many entre Medicament et Categorie
medicament_categorie = Table(
    'medicament_categorie', Base.metadata,
    Column('medicament_id', Integer, ForeignKey('medicament.id'), primary_key=True),
    Column('categorie_id', Integer, ForeignKey('categorie.id'), primary_key=True)
)

class Categorie(Base):
    __tablename__ = 'categorie'
    id = Column(Integer, primary_key=True, index=True)
    nom = Column(String(255), index=True)
    description = Column(String(255))
    
    # Relation many-to-many avec Medicament
    medicaments = relationship("Medicament", secondary=medicament_categorie, back_populates="categories")

class Medicament(Base):
    __tablename__ = 'medicament'
    id = Column(Integer, primary_key=True, index=True)
    nom = Column(String(255), index=True)
    description = Column(String(1000))
    prix_unitaire = Float()
    forme = Column(String(100))
    dosage = Column(String(100))
    ordonnance_requise = Column(Boolean, default=False)
    date_creation = Column(DateTime, default=datetime.now)
    date_mise_a_jour = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    
    # Relations
    stock = relationship("Stock", uselist=False, back_populates="medicament")
    images = relationship("ImageMedicament", back_populates="medicament")
    categories = relationship("Categorie", secondary=medicament_categorie, back_populates="medicaments")

class Stock(Base):
    __tablename__ = 'stock'
    id = Column(Integer, primary_key=True, index=True)
    medicament_id = Column(Integer, ForeignKey('medicament.id'), unique=True)
    quantite = Column(Integer)
    seuil_alerte = Column(Integer)
    emplacement = Column(String(255))
    date_peremption = Column(Date)
    lot_numero = Column(String(100))
    date_mise_a_jour = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    
    # Relation one-to-one avec Medicament
    medicament = relationship("Medicament", back_populates="stock")

class ImageMedicament(Base):
    __tablename__ = "images_medicaments"
    id = Column(Integer, primary_key=True, index=True)
    medicament_id = Column(Integer, ForeignKey("medicament.id"))
    url_image = Column(String(255))  # Added length specification
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    medicament = relationship("Medicament", back_populates="images")

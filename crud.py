from sqlalchemy.orm import Session
from sqlalchemy import func, or_, and_, desc
from datetime import date, datetime, timedelta
from typing import List, Optional
import os
from fastapi import UploadFile
import shutil

from models import Medicament, Categorie, Stock, ImageMedicament
import schemas
import models

# -------------------- GESTION DES CATÉGORIES --------------------

def create_categorie(db: Session, categorie: schemas.CategorieCreate):
    db_categorie = Categorie(**categorie.model_dump())
    db.add(db_categorie)
    db.commit()
    db.refresh(db_categorie)
    return db_categorie

def get_categorie(db: Session, categorie_id: int):
    return db.query(Categorie).filter(Categorie.id == categorie_id).first()

def get_all_categories(db: Session, skip: int = 0, limit: int = 100):
    return db.query(Categorie).offset(skip).limit(limit).all()

def update_categorie(db: Session, categorie_id: int, categorie: schemas.CategorieCreate):
    db_categorie = db.query(Categorie).filter(Categorie.id == categorie_id).first()
    if db_categorie:
        for key, value in categorie.model_dump().items():
            setattr(db_categorie, key, value)
        db.commit()
        db.refresh(db_categorie)
    return db_categorie

def delete_categorie(db: Session, categorie_id: int):
    db_categorie = db.query(Categorie).filter(Categorie.id == categorie_id).first()
    if db_categorie:
        db.delete(db_categorie)
        db.commit()
    return db_categorie

# -------------------- GESTION DES MÉDICAMENTS --------------------

def create_medicament(db: Session, medicament: schemas.MedicamentCreate):
    # Extraire les IDs de catégorie
    categorie_ids = medicament.categorie_ids
    medicament_data = medicament.model_dump(exclude={"categorie_ids"})
    
    # Créer le médicament
    db_medicament = Medicament(**medicament_data)
    db.add(db_medicament)
    db.commit()
    
    # Ajouter les catégories
    if categorie_ids:
        categories = db.query(Categorie).filter(Categorie.id.in_(categorie_ids)).all()
        db_medicament.categories = categories
        db.commit()
    
    db.refresh(db_medicament)
    return db_medicament

def get_all_medicaments(db: Session, skip: int = 0, limit: int = 100):
    return db.query(Medicament).offset(skip).limit(limit).all()

def get_medicaments_by_categorie(db: Session, categorie_id: int, skip: int = 0, limit: int = 100):
    categorie = db.query(Categorie).filter(Categorie.id == categorie_id).first()
    if not categorie:
        return []
    return categorie.medicaments[skip:skip+limit]

def update_medicament(db: Session, medicament_id: int, medicament: schemas.MedicamentCreate):
    db_medicament = db.query(Medicament).filter(Medicament.id == medicament_id).first()
    if not db_medicament:
        return None
    
    # Extraire les IDs de catégorie
    categorie_ids = medicament.categorie_ids
    medicament_data = medicament.model_dump(exclude={"categorie_ids"})
    
    # Mettre à jour les données du médicament
    for key, value in medicament_data.items():
        setattr(db_medicament, key, value)
    
    # Mettre à jour les catégories si spécifiées
    if categorie_ids is not None:
        categories = db.query(Categorie).filter(Categorie.id.in_(categorie_ids)).all()
        db_medicament.categories = categories
    
    db_medicament.date_mise_a_jour = datetime.now()
    db.commit()
    db.refresh(db_medicament)
    return db_medicament

def delete_medicament(db: Session, medicament_id: int):
    db_medicament = db.query(Medicament).filter(Medicament.id == medicament_id).first()
    if db_medicament:
        db.delete(db_medicament)
        db.commit()
    return db_medicament

def search_medicaments(db: Session, keyword: str, skip: int = 0, limit: int = 100):
    """Rechercher des médicaments par nom ou description"""
    return db.query(Medicament).filter(
        or_(
            Medicament.nom.ilike(f"%{keyword}%"),
            Medicament.description.ilike(f"%{keyword}%")
        )
    ).offset(skip).limit(limit).all()

# -------------------- GESTION DES STOCKS --------------------

def create_stock(db: Session, stock: schemas.StockCreate):
    db_stock = Stock(**stock.model_dump())
    db.add(db_stock)
    db.commit()
    db.refresh(db_stock)
    return db_stock

def get_stock(db: Session, medicament_id: int):
    return db.query(Stock).filter(Stock.medicament_id == medicament_id).first()

def get_all_stocks(db: Session, skip: int = 0, limit: int = 100):
    return db.query(Stock).offset(skip).limit(limit).all()

def update_stock(db: Session, medicament_id: int, stock: schemas.StockUpdate):
    db_stock = db.query(Stock).filter(Stock.medicament_id == medicament_id).first()
    if db_stock:
        # Ne mettre à jour que les champs fournis
        update_data = stock.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            if value is not None:  # Ignorer les valeurs None
                setattr(db_stock, key, value)
        
        db_stock.date_mise_a_jour = datetime.now()
        db.commit()
        db.refresh(db_stock)
    return db_stock

def get_stocks_sous_seuil(db: Session):
    """Récupère tous les médicaments dont le stock est inférieur au seuil d'alerte"""
    return db.query(Stock).filter(Stock.quantite <= Stock.seuil_alerte).all()

def get_stocks_proche_peremption(db: Session, jours: int = 30):
    """Récupère tous les médicaments dont la date de péremption approche"""
    date_limite = date.today() + timedelta(days=jours)
    return db.query(Stock).filter(Stock.date_peremption <= date_limite).all()

# -------------------- GESTION DES IMAGES --------------------

def get_medicament(db: Session, medicament_id: int):
    return db.query(models.Medicament).filter(models.Medicament.id == medicament_id).first()

def create_image_medicament(db: Session, image: schemas.ImageMedicamentCreate):
    # Vérifier que le médicament existe
    medicament = db.query(models.Medicament).filter(models.Medicament.id == image.medicament_id).first()
    if not medicament:
        raise ValueError("Médicament non trouvé")
    db_image = models.ImageMedicament(**image.dict())
    db.add(db_image)
    db.commit()
    db.refresh(db_image)
    return db_image

def get_all_images_medicament(db: Session, medicament_id: int):
    return db.query(models.ImageMedicament).filter(
        models.ImageMedicament.medicament_id == medicament_id
    ).all()

def get_image_medicament(db: Session, image_id: int):
    return db.query(models.ImageMedicament).filter(
        models.ImageMedicament.id == image_id
    ).first()

def delete_image_medicament(db: Session, image_id: int):
    db.query(models.ImageMedicament).filter(
        models.ImageMedicament.id == image_id
    ).delete()
    db.commit()
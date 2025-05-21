from pydantic import BaseModel, Field, validator
from typing import List, Optional
from datetime import date, datetime

# -------------------- CATÉGORIE --------------------

class CategorieBase(BaseModel):
    nom: str = Field(..., min_length=1, max_length=255, example="Antibiotiques")
    description: str = Field(..., min_length=1, max_length=1000, example="Médicaments pour traiter les infections bactériennes")

class CategorieCreate(CategorieBase):
    pass

class CategorieResponse(CategorieBase):
    id: int
    
    class Config:
        from_attributes = True

# -------------------- MÉDICAMENT --------------------

class MedicamentBase(BaseModel):
    nom: str = Field(..., min_length=1, max_length=255, example="Amoxicilline")
    description: str = Field(..., min_length=1, max_length=1000, example="Antibiotique à large spectre")
    prix_unitaire: float = Field(..., gt=0, example=15.50)
    forme: str = Field(..., min_length=1, max_length=100, example="Comprimé")
    dosage: str = Field(..., min_length=1, max_length=100, example="500mg")
    ordonnance_requise: bool = Field(default=False, example=True)

class MedicamentCreate(MedicamentBase):
    categorie_ids: List[int] = Field(default=[], example=[1, 2])  # IDs des catégories

class MedicamentResponse(MedicamentBase):
    id: int
    date_creation: datetime
    date_mise_a_jour: datetime
    
    class Config:
        from_attributes = True

class MedicamentWithStock(MedicamentResponse):
    stock: Optional['StockResponse'] = None
    categories: List['CategorieResponse'] = []
    images: List['ImageMedicamentResponse'] = []
    
    class Config:
        from_attributes = True

# -------------------- STOCK --------------------

class StockBase(BaseModel):
    medicament_id: int = Field(..., example=1)
    quantite: int = Field(..., ge=0, example=100)
    seuil_alerte: int = Field(..., ge=0, example=20)
    emplacement: str = Field(..., min_length=1, max_length=255, example="Étagère A-3")
    date_peremption: date = Field(..., example="2025-12-31")
    lot_numero: str = Field(..., min_length=1, max_length=100, example="LOT12345")

class StockCreate(StockBase):
    pass

class StockUpdate(BaseModel):
    quantite: Optional[int] = Field(None, ge=0, example=120)
    seuil_alerte: Optional[int] = Field(None, ge=0, example=25)
    emplacement: Optional[str] = Field(None, min_length=1, max_length=255, example="Étagère B-2")
    date_peremption: Optional[date] = Field(None, example="2026-01-15")
    lot_numero: Optional[str] = Field(None, min_length=1, max_length=100, example="LOT67890")

class StockResponse(StockBase):
    id: int
    date_mise_a_jour: datetime
    
    class Config:
        from_attributes = True

# -------------------- IMAGE MÉDICAMENT --------------------

class ImageMedicamentBase(BaseModel):
    medicament_id: int
    url_image: str

class ImageMedicamentCreate(ImageMedicamentBase):
    pass

class ImageMedicamentResponse(ImageMedicamentBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True

class MessageResponse(BaseModel):
    message: str

# Résoudre les références circulaires
MedicamentWithStock.model_rebuild()
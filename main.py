import shutil
from fastapi import FastAPI, Depends, HTTPException, Query, Path, UploadFile, File
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import date, datetime
from DBB import engine, get_db
import models
import schemas
import crud
import os
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from file_manager import save_file, delete_file
from fastapi.middleware.cors import CORSMiddleware



# Créer les tables dans la base de données
models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="Pharmacie API", description="API pour la gestion d'une pharmacie")

@app.get("/", response_model=dict)
def read_root():
    return {"message": "API Pharmacie est en ligne"}

# Configurer CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Autorise toutes les origines pour le développement. En production, remplacez par ["http://votre-frontend.com"]
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# -------------------- CATÉGORIES --------------------
@app.post("/categories/", response_model=schemas.CategorieResponse, tags=["Categories"])
def create_categorie_endpoint(categorie: schemas.CategorieCreate, db: Session = Depends(get_db)):
    """Créer une nouvelle catégorie de médicaments"""
    return crud.create_categorie(db, categorie)

@app.get("/categories/{categorie_id}", response_model=schemas.CategorieResponse, tags=["Categories"])
def read_categorie(categorie_id: int, db: Session = Depends(get_db)):
    """Obtenir les détails d'une catégorie spécifique"""
    db_categorie = crud.get_categorie(db, categorie_id)
    if db_categorie is None:
        raise HTTPException(status_code=404, detail="Catégorie non trouvée")
    return db_categorie

@app.get("/categories/", response_model=List[schemas.CategorieResponse], tags=["Categories"])
def read_categories(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """Obtenir la liste de toutes les catégories"""
    categories = crud.get_all_categories(db, skip=skip, limit=limit)
    return categories

@app.put("/categories/{categorie_id}", response_model=schemas.CategorieResponse, tags=["Categories"])
def update_categorie_endpoint(categorie_id: int, categorie: schemas.CategorieCreate, db: Session = Depends(get_db)):
    """Mettre à jour une catégorie existante"""
    db_categorie = crud.update_categorie(db, categorie_id, categorie)
    if db_categorie is None:
        raise HTTPException(status_code=404, detail="Catégorie non trouvée")
    return db_categorie

@app.delete("/categories/{categorie_id}", response_model=schemas.CategorieResponse, tags=["Categories"])
def delete_categorie_endpoint(categorie_id: int, db: Session = Depends(get_db)):
    """Supprimer une catégorie"""
    db_categorie = crud.delete_categorie(db, categorie_id)
    if db_categorie is None:
        raise HTTPException(status_code=404, detail="Catégorie non trouvée")
    return db_categorie

# -------------------- MÉDICAMENTS --------------------
@app.post("/medicaments/", response_model=schemas.MedicamentResponse, tags=["Medicaments"])
def create_medicament_endpoint(medicament: schemas.MedicamentCreate, db: Session = Depends(get_db)):
    """Créer un nouveau médicament"""
    return crud.create_medicament(db, medicament)

@app.get("/medicaments/{medicament_id}", response_model=schemas.MedicamentWithStock, tags=["Medicaments"])
def read_medicament(medicament_id: int, db: Session = Depends(get_db)):
    """Obtenir les détails d'un médicament spécifique avec son stock"""
    db_medicament = crud.get_medicament(db, medicament_id)
    if db_medicament is None:
        raise HTTPException(status_code=404, detail="Médicament non trouvé")
    return db_medicament

@app.get("/medicaments/", response_model=List[schemas.MedicamentResponse], tags=["Medicaments"])
def read_medicaments(
    skip: int = 0, 
    limit: int = 100, 
    categorie_id: Optional[int] = None,
    db: Session = Depends(get_db)
):
    """
    Obtenir la liste des médicaments
    - categorie_id: filtrer par catégorie
    """
    if categorie_id:
        return crud.get_medicaments_by_categorie(db, categorie_id, skip, limit)
    return crud.get_all_medicaments(db, skip=skip, limit=limit)

@app.put("/medicaments/{medicament_id}", response_model=schemas.MedicamentResponse, tags=["Medicaments"])
def update_medicament_endpoint(medicament_id: int, medicament: schemas.MedicamentCreate, db: Session = Depends(get_db)):
    """Mettre à jour un médicament existant"""
    db_medicament = crud.update_medicament(db, medicament_id, medicament)
    if db_medicament is None:
        raise HTTPException(status_code=404, detail="Médicament non trouvé")
    return db_medicament

@app.delete("/medicaments/{medicament_id}", response_model=schemas.MedicamentResponse, tags=["Medicaments"])
def delete_medicament_endpoint(medicament_id: int, db: Session = Depends(get_db)):
    """Supprimer un médicament"""
    db_medicament = crud.delete_medicament(db, medicament_id)
    if db_medicament is None:
        raise HTTPException(status_code=404, detail="Médicament non trouvé")
    return db_medicament

@app.get("/medicaments/search/", response_model=List[schemas.MedicamentResponse], tags=["Medicaments"])
def search_medicaments_endpoint(
    q: str = Query(..., min_length=1, description="Terme de recherche"),
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """
    Rechercher des médicaments par nom ou description
    """
    medicaments = crud.search_medicaments(db, q, skip, limit)
    return medicaments

# -------------------- STOCK --------------------
@app.post("/stocks/", response_model=schemas.StockResponse, tags=["Stocks"])
def create_stock_endpoint(stock: schemas.StockCreate, db: Session = Depends(get_db)):
    """Créer ou mettre à jour le stock d'un médicament"""
    medicament = crud.get_medicament(db, stock.medicament_id)
    if not medicament:
        raise HTTPException(status_code=404, detail="Médicament non trouvé")
    return crud.create_stock(db, stock)

@app.get("/stocks/{medicament_id}", response_model=schemas.StockResponse, tags=["Stocks"])
def read_stock(medicament_id: int, db: Session = Depends(get_db)):
    """Obtenir les détails du stock d'un médicament spécifique"""
    db_stock = crud.get_stock(db, medicament_id)
    if db_stock is None:
        raise HTTPException(status_code=404, detail="Stock non trouvé pour ce médicament")
    return db_stock

@app.get("/stocks/", response_model=List[schemas.StockResponse], tags=["Stocks"])
def read_stocks(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """Obtenir la liste de tous les stocks"""
    stocks = crud.get_all_stocks(db, skip=skip, limit=limit)
    return stocks

@app.put("/stocks/{medicament_id}", response_model=schemas.StockResponse, tags=["Stocks"])
def update_stock_endpoint(medicament_id: int, stock: schemas.StockUpdate, db: Session = Depends(get_db)):
    """Mettre à jour le stock d'un médicament existant"""
    db_stock = crud.update_stock(db, medicament_id, stock)
    if db_stock is None:
        raise HTTPException(status_code=404, detail="Stock non trouvé pour ce médicament")
    return db_stock

@app.get("/stocks/alerte/seuil", response_model=List[schemas.StockResponse], tags=["Stocks"])
def get_stock_alertes_endpoint(db: Session = Depends(get_db)):
    """Obtenir la liste des médicaments dont le stock est inférieur au seuil d'alerte"""
    return crud.get_stocks_sous_seuil(db)

# -------------------- CONFIGURATION DOSSIERS --------------------
UPLOAD_BASE_DIR = "Uploads"
MEDICAMENT_IMAGE_DIR = os.path.join(UPLOAD_BASE_DIR, "medicaments")
os.makedirs(MEDICAMENT_IMAGE_DIR, exist_ok=True)

# Taille maximale du fichier (10MB)
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB
ALLOWED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp"}

# -------------------- ENDPOINTS IMAGES --------------------
@app.post("/medicaments/{medicament_id}/upload-image/", 
         response_model=schemas.ImageMedicamentResponse,
         tags=["Medicaments"],
         summary="Uploader une image pour un médicament",
         include_in_schema=True)
async def upload_medicament_image(
    medicament_id: int,
    file: UploadFile = File(..., description="Cliquez pour sélectionner une image (JPG/PNG/WEBP)"),
    db: Session = Depends(get_db)
):
    """
    Upload une image pour un médicament spécifique.
    
    Utilisation:
    1. Cliquez sur 'Try it out'
    2. Utilisez le sélecteur de fichiers
    3. Cliquez sur 'Execute'
    """
    medicament = crud.get_medicament(db, medicament_id)
    if not medicament:
        raise HTTPException(status_code=404, detail="Médicament non trouvé")

    file_ext = os.path.splitext(file.filename)[1].lower()
    if file_ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400, 
            detail=f"Formats acceptés: {', '.join(ALLOWED_EXTENSIONS)}"
        )

    try:
        file.file.seek(0, 2)
        file_size = file.file.tell()
        file.file.seek(0)
        if file_size > MAX_FILE_SIZE:
            raise HTTPException(
                status_code=400,
                detail=f"Taille max: {MAX_FILE_SIZE//(1024*1024)}MB"
            )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    medicament_dir = os.path.join(MEDICAMENT_IMAGE_DIR, str(medicament_id))
    os.makedirs(medicament_dir, exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{timestamp}{file_ext}"
    file_path = os.path.join(medicament_dir, filename)

    try:
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
    except IOError as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        await file.close()

    try:
        image_data = schemas.ImageMedicamentCreate(
            medicament_id=medicament_id,
            url_image=f"/Uploads/medicaments/{medicament_id}/{filename}"
        )
        db_image = crud.create_image_medicament(db, image_data)
    except Exception as e:
        if os.path.exists(file_path):
            os.remove(file_path)
        raise HTTPException(status_code=500, detail=str(e))
    
    return db_image

@app.get("/api/medicaments/{medicament_id}/images/{filename}",
         response_class=FileResponse,
         tags=["Medicaments"],
         summary="Récupérer une image de médicament",
         include_in_schema=True)
async def serve_medicament_image(
    medicament_id: int,
    filename: str
):
    file_path = os.path.join(MEDICAMENT_IMAGE_DIR, str(medicament_id), filename)
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="Image non trouvée")
    return FileResponse(file_path)

@app.get("/medicaments/{medicament_id}/images/", 
         response_model=List[schemas.ImageMedicamentResponse],
         tags=["Medicaments"],
         summary="Lister les images d'un médicament",
         include_in_schema=True)
def get_medicament_images(
    medicament_id: int,
    db: Session = Depends(get_db)
):
    """
    Récupérer toutes les images d'un médicament.
    
    - **medicament_id**: ID du médicament
    """
    if not crud.get_medicament(db, medicament_id):
        raise HTTPException(status_code=404, detail="Médicament non trouvé")
    return crud.get_all_images_medicament(db, medicament_id)

@app.delete("/images/{image_id}",
           response_model=schemas.MessageResponse,
           tags=["Medicaments"],
           summary="Supprimer une image de médicament",
           include_in_schema=True)
def delete_medicament_image(
    image_id: int,
    db: Session = Depends(get_db)
):
    """
    Supprimer une image de médicament.
    
    - **image_id**: ID de l'image à supprimer
    """
    image = crud.get_image_medicament(db, image_id)
    if not image:
        raise HTTPException(status_code=404, detail="Image non trouvée")

    try:
        url_parts = image.url_image.split('/')
        if len(url_parts) < 4:
            raise ValueError("URL d'image invalide")
        
        filename = url_parts[-1]
        medicament_id = url_parts[-2]
        file_path = os.path.join(MEDICAMENT_IMAGE_DIR, medicament_id, filename)

        if os.path.exists(file_path):
            os.remove(file_path)
    except Exception as e:
        raise HTTPException(
            status_code=500, 
            detail=f"Erreur lors de la suppression du fichier: {str(e)}"
        )

    crud.delete_image_medicament(db, image_id)
    return {"message": "Image supprimée avec succès"}

# -------------------- FIN DE LA GESTION DES IMAGES --------------------
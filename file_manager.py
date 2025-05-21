import os
import shutil
from fastapi import UploadFile
from typing import Optional
from datetime import datetime
import logging

# Configurer la journalisation
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Répertoire de stockage des fichiers
UPLOAD_DIR = "Uploads"

# Créer le répertoire s'il n'existe pas
if not os.path.exists(UPLOAD_DIR):
    os.makedirs(UPLOAD_DIR)

def save_file(file: UploadFile, product_id: int) -> Optional[str]:
    """
    Sauvegarde un fichier dans le répertoire local et retourne le chemin du fichier.
    """
    try:
        # Validation de l'extension du fichier
        allowed_extensions = {".jpg", ".jpeg", ".png", ".webp"}
        file_ext = os.path.splitext(file.filename)[1].lower()
        if file_ext not in allowed_extensions:
            raise ValueError("Formats acceptés: JPG, PNG, WEBP")

        # Créer un sous-répertoire pour le produit s'il n'existe pas
        product_dir = os.path.join(UPLOAD_DIR, str(product_id))
        if not os.path.exists(product_dir):
            os.makedirs(product_dir)

        # Générer un nom de fichier unique
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{timestamp}{file_ext}"
        file_path = os.path.join(product_dir, filename)

        # Sauvegarder le fichier
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        return file_path
    except Exception as e:
        logger.error(f"Erreur lors de la sauvegarde du fichier {file.filename}: {e}")
        raise

def delete_file(file_path: str) -> bool:
    """
    Supprime un fichier du répertoire local.
    """
    try:
        if os.path.exists(file_path):
            os.remove(file_path)
            logger.info(f"Fichier supprimé: {file_path}")
            return True
        logger.warning(f"Fichier non trouvé: {file_path}")
        return False
    except Exception as e:
        logger.error(f"Erreur lors de la suppression du fichier {file_path}: {e}")
        raise
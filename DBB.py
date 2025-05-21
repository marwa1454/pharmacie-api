from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os

# Déterminer si l'application est dans Docker (via une variable d'environnement)
IS_DOCKER = os.getenv("IS_DOCKER", "false").lower() == "true"

# Définir l'URL de la base de données selon l'environnement
DEFAULT_DATABASE_URL = (
    "mysql+pymysql://Marwa:Marwa77233473@db:3306/DBB" if IS_DOCKER
    else "mysql+pymysql://Marwa:Marwa77233473@localhost:3307/DBB"
)
DATABASE_URL = os.getenv("DATABASE_URL", DEFAULT_DATABASE_URL)

# Création du moteur SQLAlchemy
engine = create_engine(DATABASE_URL)

# Création d'une session locale
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base pour les modèles déclaratifs
Base = declarative_base()

# Fonction pour obtenir une session de base de données
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
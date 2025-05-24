import os
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker
from dotenv import load_dotenv

# Charger le fichier .env
load_dotenv()

# Récupérer les variables d'environnement
DB_USERNAME = os.getenv("DB_USERNAME")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_NAME = os.getenv("DB_NAME")

# Vérifier que les variables sont définies
if not all([DB_USERNAME, DB_PASSWORD, DB_NAME]):
    raise ValueError("Les variables d'environnement DB_USERNAME, DB_PASSWORD ou DB_NAME ne sont pas définies.")

# Définir la DATABASE_URL
DATABASE_URL = f"mysql+pymysql://{DB_USERNAME}:{DB_PASSWORD}@db:3306/{DB_NAME}"

# Créer le moteur SQLAlchemy
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
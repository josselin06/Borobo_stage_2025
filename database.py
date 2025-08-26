from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from app.config import settings

# Récupère l'URL de connexion depuis la config
DATABASE_URL = settings.DATABASE_URL

# Crée le moteur SQLAlchemy (sans connect_args)
engine = create_engine(DATABASE_URL)

# Initialise la session
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base des modèles SQLAlchemy
Base = declarative_base()

# Dépendance pour FastAPI : session DB
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()



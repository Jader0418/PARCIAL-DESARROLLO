from sqlmodel import SQLModel, create_engine, Session
import os
from dotenv import load_dotenv

# ✅ Importar desde el ARCHIVO models.py
from models import Estudiante, Curso, Matricula

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///universidad.db")
engine = create_engine(DATABASE_URL, echo=True)

def create_db_and_tables():
    SQLModel.metadata.create_all(engine)

def get_session():
    with Session(engine) as session:
        yield session
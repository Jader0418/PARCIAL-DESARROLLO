"""
CONFIGURACIÓN DE BASE DE DATOS Y CONEXIÓN
"""
# Importar SQLModel para modelos y motor de BD
from sqlmodel import SQLModel, create_engine, Session
# Importar sistema operativo para variables de entorno
import os
# Importar para cargar archivo .env
from dotenv import load_dotenv

# 🔄 IMPORTAR TODOS LOS MODELOS para que SQLModel los reconozca
# Esto es NECESARIO para que create_all() cree las tablas
from models.estudiante import Estudiante
from models.curso import Curso
from models.matricula import Matricula

# 📁 CARGAR variables de entorno desde archivo .env
load_dotenv()

# 🔗 URL de conexión a la base de datos
# Usa variable de entorno o valor por defecto (SQLite)
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///universidad.db")

# 🚀 CREAR motor de base de datos
# echo=True muestra las consultas SQL en consola (útil para desarrollo)
engine = create_engine(DATABASE_URL, echo=True)

def create_db_and_tables():
    """
    CREAR todas las tablas en la base de datos
    Basado en los modelos SQLModel definidos
    """
    SQLModel.metadata.create_all(engine)

def get_session():
    """
    GENERAR sesión de base de datos para dependencias de FastAPI
    Usado con Depends() en los endpoints
    """
    # Context manager: abre y cierra sesión automáticamente
    with Session(engine) as session:
        # yield permite usar la sesión y luego cerrarla
        yield session

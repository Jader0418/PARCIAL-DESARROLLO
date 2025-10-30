"""
💾 CONFIGURACIÓN DE BASE DE DATOS
Maneja la conexión a la base de datos y la creación de tablas
"""

from sqlmodel import SQLModel, create_engine, Session  # 🗄️ Motor y sesiones de BD
import os  # 🖥️  Para variables de entorno
from dotenv import load_dotenv  # 🔐  Para cargar .env

# 🔄 IMPORTAR MODELOS: Necesario para que SQLModel reconozca las tablas
from models import Estudiante, Curso, Matricula

# 🔐 CARGAR variables de entorno desde archivo .env
load_dotenv()

# 🌐 URL DE CONEXIÓN A BASE DE DATOS
# - Usa variable de entorno DATABASE_URL o valor por defecto (SQLite)
# - sqlite:/// para SQLite (archivo local)
# - postgresql:// para PostgreSQL (producción)
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///universidad.db")

# 🚀 CREAR motor de base de datos
# - echo=True: Muestra las consultas SQL en consola (útil para desarrollo)
# - echo=False: No muestra consultas (producción)
engine = create_engine(DATABASE_URL, echo=True)


def create_db_and_tables():
    """
    🏗️ CREAR todas las tablas en la base de datos

    📋 FUNCIONALIDAD:
    - Crea las tablas basándose en los modelos SQLModel
    - Solo crea tablas que no existan
    - Ejecutar al iniciar la aplicación
    """
    SQLModel.metadata.create_all(engine)


def get_session():
    """
    🔄 GENERAR sesión de base de datos

    📋 USO:
    - Para dependencias de FastAPI (Depends)
    - Maneja automáticamente apertura y cierre de sesión
    - Context manager: with Session(engine) as session:

    🎯 RETORNA:
    - Generator[Session]: Sesión de base de datos lista para usar
    """
    with Session(engine) as session:
        yield session  # 📤 Entrega la sesión y luego la cierra automáticamente
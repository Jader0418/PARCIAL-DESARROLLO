from sqlmodel import SQLModel, Field, Relationship
from typing import List, Optional
from pydantic import validator
import re


# 📝 TABLA INTERMEDIA - debe definirse PRIMERO
class Matricula(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    estudiante_id: int = Field(foreign_key="estudiante.id")
    curso_id: int = Field(foreign_key="curso.id")


# 🎓 MODELO ESTUDIANTE
class Estudiante(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    cedula: str = Field(index=True, unique=True)
    nombre: str
    email: str
    semestre: int = Field(ge=1, le=12)

    # 🔗 RELACIÓN - usar la CLASE directamente, no string
    cursos: List["Curso"] = Relationship(back_populates="estudiantes", link_model=Matricula)

    @validator('cedula')
    def validar_cedula(cls, v):
        if not re.match(r'^\d{8,10}$', v):
            raise ValueError('La cédula debe tener entre 8 y 10 dígitos')
        return v

    @validator('email')
    def validar_email(cls, v):
        if not re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', v):
            raise ValueError('Formato de email inválido')
        return v


# 📚 MODELO CURSO
class Curso(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    codigo: str = Field(index=True, unique=True)
    nombre: str
    creditos: int = Field(ge=1, le=6)
    horario: str

    # 🔗 RELACIÓN - usar la CLASE directamente
    estudiantes: List[Estudiante] = Relationship(back_populates="cursos", link_model=Matricula)

    @validator('codigo')
    def validar_codigo(cls, v):
        if not re.match(r'^[A-Z]{3}\d{3}$', v):
            raise ValueError('El código debe tener formato: AAA111')
        return v

    @validator('horario')
    def validar_horario(cls, v):
        if len(v) < 5:
            raise ValueError('Formato de horario inválido')
        return v
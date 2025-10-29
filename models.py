from sqlmodel import SQLModel, Field, Relationship
from typing import List, Optional
from datetime import time
from pydantic import validator, EmailStr
import re


# Tabla intermedia para la relación N:M
class Matricula(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    estudiante_id: int = Field(foreign_key="estudiante.id")
    curso_id: int = Field(foreign_key="curso.id")


class Estudiante(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    cedula: str = Field(index=True, unique=True)
    nombre: str
    email: str
    semestre: int = Field(ge=1, le=12)

    # Relación con cursos a través de Matricula
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


class Curso(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    codigo: str = Field(index=True, unique=True)
    nombre: str
    creditos: int = Field(ge=1, le=6)
    horario: str  # Formato: "Lunes 8:00-10:00"

    # Relación con estudiantes a través de Matricula
    estudiantes: List[Estudiante] = Relationship(back_populates="cursos", link_model=Matricula)

    @validator('codigo')
    def validar_codigo(cls, v):
        if not re.match(r'^[A-Z]{3}\d{3}$', v):
            raise ValueError('El código debe tener formato: AAA111')
        return v

    @validator('horario')
    def validar_horario(cls, v):
        # Validación simple del formato del horario
        if len(v) < 5:
            raise ValueError('Formato de horario inválido')
        return v
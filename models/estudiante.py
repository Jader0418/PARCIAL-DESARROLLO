"""
Modelo Estudiante
"""
from sqlmodel import Field, Relationship
from typing import List, Optional
from pydantic import validator
from .base import ModeloBase, ValidacionesBase


class Estudiante(ModeloBase, ValidacionesBase, table=True):
    cedula: str = Field(index=True, unique=True)
    nombre: str
    email: str
    semestre: int = Field(ge=1, le=12)

    cursos: List["Curso"] = Relationship(
        back_populates="estudiantes",
        link_model="Matricula"
    )

    @validator('cedula')
    def validar_cedula_estudiante(cls, v):
        return cls.validar_cedula(v)

    @validator('email')
    def validar_email_estudiante(cls, v):
        return cls.validar_email(v)

    def __repr__(self):
        return f"<Estudiante(id={self.id}, nombre='{self.nombre}', cedula='{self.cedula}')>"


# Importación circular al final
from .curso import Curso
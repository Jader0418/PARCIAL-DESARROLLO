"""
Modelo Curso
"""
from sqlmodel import Field, Relationship
from typing import List, Optional
from pydantic import validator
from .base import ModeloBase, ValidacionesBase


class Curso(ModeloBase, ValidacionesBase, table=True):
    codigo: str = Field(index=True, unique=True)
    nombre: str
    creditos: int = Field(ge=1, le=6)
    horario: str

    estudiantes: List["Estudiante"] = Relationship(
        back_populates="cursos",
        link_model="Matricula"
    )

    @validator('codigo')
    def validar_codigo_curso(cls, v):
        return cls.validar_codigo_curso(v)

    @validator('horario')
    def validar_horario(cls, v):
        if len(v.strip()) < 5:
            raise ValueError('El horario debe tener al menos 5 caracteres')
        return v.strip()

    def __repr__(self):
        return f"<Curso(id={self.id}, codigo='{self.codigo}', nombre='{self.nombre}')>"


# Importación circular al final
from .estudiante import Estudiante

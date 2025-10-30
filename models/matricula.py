"""
Modelo Matricula - Tabla intermedia
"""
from sqlmodel import Field
from .base import ModeloBase


class Matricula(ModeloBase, table=True):
    estudiante_id: int = Field(foreign_key="estudiante.id")
    curso_id: int = Field(foreign_key="curso.id")

    def __repr__(self):
        return f"<Matricula(estudiante_id={self.estudiante_id}, curso_id={self.curso_id})>"
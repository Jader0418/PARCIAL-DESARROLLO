"""
Clases base y validaciones comunes
"""
from sqlmodel import SQLModel, Field
from typing import Optional
from pydantic import validator
import re


class ModeloBase(SQLModel):
    id: Optional[int] = Field(default=None, primary_key=True)


class ValidacionesBase:
    @staticmethod
    def validar_cedula(v: str) -> str:
        if not re.match(r'^\d{8,10}$', v):
            raise ValueError('La cédula debe tener entre 8 y 10 dígitos')
        return v

    @staticmethod
    def validar_email(v: str) -> str:
        if not re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', v):
            raise ValueError('Formato de email inválido')
        return v

    @staticmethod
    def validar_codigo_curso(v: str) -> str:
        if not re.match(r'^[A-Z]{3}\d{3}$', v):
            raise ValueError('El código debe tener formato: AAA111')
        return v
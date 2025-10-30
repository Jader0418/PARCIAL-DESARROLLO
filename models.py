"""
- MODELOS DE DATOS: Define la estructura completa de la base de datos para el sistema universitario

FUNCIONALIDADES:
• Modelos de datos con SQLModel
• Validaciones automáticas con Pydantic
• Relaciones entre entidades (Estudiante ↔ Curso)
• Restricciones de integridad de datos
"""

from sqlmodel import SQLModel, Field, Relationship
# SQLModel: Combina SQLAlchemy (BD) + Pydantic (validaciones)
# Field: Para definir campos de la base de datos
# Relationship: Para definir relaciones entre modelos

from typing import List, Optional
# List: Para listas de objetos (relaciones uno-a-muchos)
# Optional: Para campos opcionales

from pydantic import validator
# validator: Decorador para crear validaciones personalizadas

import re
# re: Para expresiones regulares en validaciones

class Matricula(SQLModel, table=True):
    """
    TABLA INTERMEDIA para relación Muchos-a-Muchos (N:M)

    PROPÓSITO:
    • Conectar Estudiantes con Cursos
    • Registrar qué estudiante está en qué curso
    • Permitir que un estudiante tenga múltiples cursos
    • Permitir que un curso tenga múltiples estudiantes

    RELACIÓN: Estudiante ←→ Curso (N:M)
    """

    # CAMPO: ID único automático (clave primaria)
    id: Optional[int] = Field(
        default=None,  # Se genera automáticamente
        primary_key=True,  # Identificador único principal
        description="ID único de la matrícula en el sistema"
    )

    # CAMPO: Referencia al estudiante (clave foránea)
    estudiante_id: int = Field(
        foreign_key="estudiante.id",  # Apunta a la tabla estudiante
        description="ID del estudiante que se matricula"
    )

    # CAMPO: Referencia al curso (clave foránea)
    curso_id: int = Field(
        foreign_key="curso.id",  # Apunta a la tabla curso
        description="ID del curso en el que se matricula el estudiante"
    )

    def __repr__(self):
        """
        MÉTODO: Representación legible del objeto

        USO:
        • Debugging en consola
        • Logs de la aplicación
        • Mensajes de error

        EJEMPLO: <Matricula(estudiante_id=1, curso_id=2)>
        """
        return f"<Matricula(estudiante_id={self.estudiante_id}, curso_id={self.curso_id})>"

class Estudiante(SQLModel, table=True):
    """
    PROPOSITO:
    • Almacenar información personal del estudiante
    • Gestionar datos académicos (semestre)
    • Mantener relaciones con los cursos matriculados
    DATOS ALMACENADOS:
    • Información de identificación (cédula, nombre, email)
    • Información académica (semestre)
    • Relación con cursos matriculados
    """

    # CAMPO: ID único automático
    id: Optional[int] = Field(
        default=None,
        primary_key=True,
        description="ID único del estudiante en el sistema"
    )

    # CAMPO: Cédula de identidad (única en el sistema)
    cedula: str = Field(
        index=True,  # Crea índice para búsquedas rápidas
        unique=True,  # Garantiza que no haya cédulas duplicadas
        description="Cédula de identidad del estudiante (8-10 dígitos)"
    )

    # CAMPO: Nombre completo del estudiante
    nombre: str = Field(
        description="Nombre completo del estudiante"
    )

    # CAMPO: Correo electrónico institucional
    email: str = Field(
        description="Dirección de correo electrónico institucional"
    )

    # CAMPO: Semestre actual del estudiante
    semestre: int = Field(
        ge=1,  # VALIDACIÓN: Valor mínimo permitido (Greater or Equal)
        le=12,  # VALIDACIÓN: Valor máximo permitido (Less or Equal)
        description="Semestre académico actual del estudiante (rango: 1-12)"
    )

    # RELACIÓN: Cursos en los que está matriculado
    cursos: List["Curso"] = Relationship(
        back_populates="estudiantes",  # Crea relación bidireccional
        link_model=Matricula,  # Usa tabla Matricula como intermedia
        # NOTA: Relationship NO acepta parámetro 'description'
    )

    @validator('cedula')
    def validar_cedula(cls, valor):
        """
        VALIDACIÓN: Formato correcto de cédula de identidad
        REGLAS DE VALIDACIÓN:
        • Solo caracteres numéricos (0-9)
        • Longitud entre 8 y 10 dígitos
        • No permite letras ni caracteres especiales
        """
        # 🔍 EXPRESIÓN REGULAR: ^ inicio, \d solo dígitos, {8,10} entre 8-10, $ fin
        if not re.match(r'^\d{8,10}$', valor):
            raise ValueError('La cédula debe contener entre 8 y 10 dígitos numéricos')
        return valor

    @validator('email')
    def validar_email(cls, valor):
        """
        VALIDACIÓN: Formato correcto de dirección de email

        REGLAS DE VALIDACIÓN:
        • usuario@dominio.extensión
        • Extensión de al menos 2 caracteres
        • Caracteres permitidos: letras, números, ., _, %, +, -
        """
        # 🔍 EXPRESIÓN REGULAR para validar formato de email estándar
        if not re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', valor):
            raise ValueError('Formato de email inválido. Use: usuario@dominio.extensión')
        return valor

    def __repr__(self):
        """
         MÉTODO: Representación legible para debugging

        USO PRINCIPAL:
        • Mensajes en consola durante desarrollo
        • Logs de la aplicación
        • Depuración de errores

         EJEMPLO: <Estudiante(id=1, nombre='Ana García', cedula='1234567890')>
        """
        return f"<Estudiante(id={self.id}, nombre='{self.nombre}', cedula='{self.cedula}')>"

class Curso(SQLModel, table=True):
    """
    MODELO CURSO - Representa un curso académico de la universidad

    PROPÓSITO:
    • Almacenar información de cursos académicos
    • Gestionar créditos y horarios
    • Mantener relación con estudiantes matriculados

    DATOS ALMACENADOS:
    • Información identificadora (código, nombre)
    • Información académica (créditos, horario)
    • Relación con estudiantes matriculados
    """

    # CAMPO: ID único automático
    id: Optional[int] = Field(
        default=None,
        primary_key=True,
        description="ID único del curso en el sistema"
    )

    # CAMPO: Código único del curso
    codigo: str = Field(
        index=True,  #  Índice para búsquedas rápidas por código
        unique=True,  # Garantiza códigos únicos (no duplicados)
        description="Código único del curso (formato: 3 letras + 3 números)"
    )

    # CAMPO: Nombre descriptivo del curso
    nombre: str = Field(
        description="Nombre completo y descriptivo del curso"
    )

    # CAMPO: Número de créditos académicos
    creditos: int = Field(
        ge=1,  # VALIDACIÓN: Mínimo 1 crédito
        le=6,  # VALIDACIÓN: Máximo 6 créditos
        description="Número de créditos académicos del curso (rango: 1-6)"
    )

    # CAMPO: Horario del curso
    horario: str = Field(
        description="Horario y días de clase. Ejemplo: 'Lunes y Miércoles 8:00-10:00'"
    )

    # RELACIÓN: Estudiantes matriculados en este curso
    estudiantes: List[Estudiante] = Relationship(
        back_populates="cursos",  # Crea relación bidireccional
        link_model=Matricula,  # Usa tabla Matricula como intermedia
        # NOTA: Relationship NO acepta parámetro 'description'
    )

    @validator('codigo')
    def validar_codigo(cls, valor):
        """
        VALIDACIÓN: Formato correcto de código de curso

        REGLAS DE VALIDACIÓN:
        • 3 letras mayúsculas (A-Z)
        • 3 números (0-9)
        • Sin espacios ni caracteres especiales
        """

        # EXPRESIÓN REGULAR: 3 letras mayúsculas + 3 números
        if not re.match(r'^[A-Z]{3}\d{3}$', valor):
            raise ValueError(' El código debe tener formato AAA111 (3 letras mayúsculas + 3 números)')
        return valor

    @validator('horario')
    def validar_horario(cls, valor):
        """
        VALIDACIÓN: Formato básico de horario

        REGLAS DE VALIDACIÓN:
        • Mínimo 5 caracteres de longitud
        • No puede estar vacío o solo espacios
        • Se eliminan espacios en blanco al inicio/final

        EJEMPLOS VÁLIDOS:
        • 'Lunes 8:00-10:00'
        • 'Martes y Jueves 14:00-16:00'
        • 'Miércoles 18:00-20:00'
        """
        valor_limpio = valor.strip()  # Limpiar espacios en blanco

        if len(valor_limpio) < 5:
            raise ValueError('El horario debe tener al menos 5 caracteres')

        return valor_limpio

    def __repr__(self):
        """
        MÉTODO: Representación legible para debugging

        EJEMPLO: <Curso(id=1, codigo='MAT101', nombre='Matemáticas Básicas')>
        """
        return f"<Curso(id={self.id}, codigo='{self.codigo}', nombre='{self.nombre}')>"



"""
ESTE ARCHIVO CONTIENE LA ESTRUCTURA COMPLETA DE LA BASE DE DATOS

RELACIONES IMPLEMENTADAS:
Estudiante ←→ Curso (Relación Muchos-a-Muchos a través de Matricula)

TABLAS CREADAS:
1. estudiante  - Información de estudiantes
2. curso       - Información de cursos  
3. matricula   - Tabla intermedia para relaciones

VALIDACIONES AUTOMÁTICAS:
• Formato de cédula (8-10 dígitos)
• Formato de email (usuario@dominio.ext)
• Formato de código de curso (AAA111)
• Rangos numéricos (semestre: 1-12, créditos: 1-6)
• Horario no vacío

USO EN LA APLICACIÓN:
from models import Estudiante, Curso, Matricula
"""
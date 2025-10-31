# ~~~~~ Sistema de Gestión Universitaria - API ~~~~

## __ Descripción __

**Sistema de Gestión Universitaria** es una API REST moderna desarrollada con FastAPI y SQLModel para la administración académica de la Universidad Católica de Colombia. Permite gestionar estudiantes, cursos y matrículas con validaciones robustas y documentación automática.

## Características Principales

- **FastAPI** - Framework web de alto rendimiento
- **SQLModel** - ORM con validaciones Pydantic integradas
- **SQLite** - Base de datos para desarrollo
- **Pydantic** - Validación de datos y serialización

### 📊 Modelos Implementados
- ** Estudiante**: Gestión de información estudiantil
- ** Curso**: Administración de oferta académica  
- ** Matricula**: Sistema de relaciones N:M entre estudiantes y cursos

### Validaciones de Negocio
- ✅ Cédula única (8-10 dígitos)
- ✅ Código de curso único (formato AAA111)
- ✅ Control de conflictos de horario
- ✅ Validación de formatos de email
- ✅ Rangos académicos (semestre 1-12, créditos 1-6)




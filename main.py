f"""
Este archivo contiene toda la lógica de la API REST que gestiona el sistema universitario.
Define los endpoints, maneja las solicitudes HTTP y coordina las operaciones de la base de datos.
"""

# FRAMEWORK FASTAPI - Para crear la API web
from fastapi import FastAPI, Depends, HTTPException, status
# • FastAPI: Clase principal del framework
# • Depends: Para inyección de dependencias (sesiones de BD)
# • HTTPException: Para manejar errores HTTP personalizados
# • status: Códigos de estado HTTP predefinidos

# SQLMODEL - Para operaciones de base de datos
from sqlmodel import Session
# • Session: Para manejar transacciones con la base de datos

# Typing - Para mejor documentación y validación
from typing import List, Optional
# • List: Para indicar que se retorna una lista de objetos
# • Optional: Para parámetros que pueden ser None

# CONFIGURACIÓN BD - Nuestros módulos personalizados
from database import get_session, create_db_and_tables
# • get_session: Función que proporciona sesiones de BD
# • create_db_and_tables: Función que crea las tablas en la BD

# MODELOS - Nuestras entidades de datos
from models import Estudiante, Curso
# • Estudiante: Modelo que representa un estudiante
# • Curso: Modelo que representa un curso académico

# OPERACIONES CRUD - Todas las funciones de negocio
from crud import (
    crear_estudiante, listar_estudiantes, obtener_estudiante,
    actualizar_estudiante, eliminar_estudiante, obtener_estudiante_con_cursos,
    crear_curso, listar_cursos, obtener_curso, actualizar_curso,
    eliminar_curso, obtener_curso_con_estudiantes, matricular_estudiante,
    desmatricular_estudiante, cursos_de_estudiante, estudiantes_de_curso
)
# • Funciones para estudiantes: CRUD completo + operaciones especializadas
# • Funciones para cursos: CRUD completo + operaciones especializadas
# • Funciones para matrículas: Gestión de relaciones entre estudiantes y cursos

app = FastAPI(
    title="------- SISTEMA DE GESTION UNIVERSITARIA -------",
    description="~~ API para la gestion de estudiantes, cursos y matriculas en la Universidad Catolica de Colombia ~~",
    version="1.0.0"
)



@app.on_event("startup")
def on_startup():

    create_db_and_tables()


#ENDPOINT
@app.post("/| PRIMIPAROS |/",
          response_model=Estudiante,
          status_code=status.HTTP_201_CREATED,
          tags=["| ESTUDIANTES |"])
def crear_estudiante(estudiante: Estudiante, session: Session = Depends(get_session)):
    """
    CREAR UN NUEVO ESTUDIANTE EN EL SISTEMA

    PARÁMETROS:
    • estudiante (body): Objeto Estudiante con los datos a crear
    • session: Sesión de BD inyectada automáticamente
    • 201 Created: Estudiante creado exitosamente
    • 400 Bad Request: Error en los datos de entrada
    """
    try:
        # Intentar crear el estudiante llamando a la función CRUD
        return crear_estudiante(session, estudiante)
    except ValueError as e:
        # Capturar errores de validación y convertirlos a HTTP 400
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/| PRIMIPAROS |/",
         response_model=List[Estudiante],
         tags=["| ESTUDIANTES |"])
def listar_estudiantes(semestre: Optional[int] = None, session: Session = Depends(get_session)):
    """
    LISTAR TODOS LOS ESTUDIANTES REGISTRADOS

    PARÁMETROS DE CONSULTA :
    • semestre : Filtrar estudiantes por semestre específico

    RESPUESTA:
    • Lista de objetos Estudiante en formato JSON
    """
    # Delegar la operación a la función CRUD correspondiente
    return listar_estudiantes(session, semestre)


@app.get("/| PRIMIPAROS |/{estudiante_id}",
         response_model=Estudiante,
         tags=["| ESTUDIANTES |"])
def obtener_estudiante(estudiante_id: int, session: Session = Depends(get_session)):
    """
    OBTENER UN ESTUDIANTE ESPECÍFICO POR SU ID

    PARÁMETROS DE RUTA:
    • estudiante_id: ID único del estudiante a buscar
    RESPUESTAS:
    • 200 OK: Estudiante encontrado y retornado
    • 404 Not Found: No existe estudiante con ese ID
    """
    # Buscar el estudiante en la base de datos
    estudiante = obtener_estudiante(session, estudiante_id)

    # Si no se encuentra, retornar error 404
    if not estudiante:
        raise HTTPException(status_code=404, detail="Estudiante no encontrado")

    # Si se encuentra, retornar el estudiante
    return estudiante


@app.get("/| PRIMIPAROS |/{estudiante_id}/cursos",
         response_model=Estudiante,
         tags=["| ESTUDIANTES |"])
def obtener_estudiante_con_cursos(estudiante_id: int, session: Session = Depends(get_session)):
    """
    OBTENER UN ESTUDIANTE CON TODOS SUS CURSOS MATRICULADOS
    CARACTERÍSTICAS:
    • Consulta relacional que incluye datos relacionados
    • Carga la lista de cursos del estudiante
    • Útil para ver el horario completo de un estudiante

    """
    # 🔍 Buscar estudiante con sus relaciones cargadas
    estudiante = obtener_estudiante_con_cursos(session, estudiante_id)

    if not estudiante:
        raise HTTPException(status_code=404, detail="Estudiante no encontrado")

    return estudiante


@app.put("/| PRIMIPAROS |/{estudiante_id}",
         response_model=Estudiante,
         tags=["| ESTUDIANTES |"])
def actualizar_estudiante(estudiante_id: int, estudiante_data: dict, session: Session = Depends(get_session)):
    """
    ACTUALIZAR LOS DATOS DE UN ESTUDIANTE EXISTENTE
    PARÁMETROS:
    • estudiante_id: ID del estudiante a actualizar
    • estudiante_data: Diccionario con los campos a modificar

    FUNCIONALIDAD:
    • Actualiza solo los campos proporcionados
    • Mantiene los campos no especificados
    • Aplica las mismas validaciones que en la creación

    """
    try:
        # Intentar actualizar el estudiante
        estudiante = actualizar_estudiante(session, estudiante_id, estudiante_data)

        if not estudiante:
            raise HTTPException(status_code=404, detail="Estudiante no encontrado")

        return estudiante
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.delete("/| PRIMIPAROS |/{estudiante_id}",
            tags=["| ESTUDIANTES |"])
def eliminar_estudiante(estudiante_id: int, session: Session = Depends(get_session)):
    """
    ADVERTENCIA:
    • Elimina también todas sus matrículas (eliminación en cascada)
    • Esta operación NO se puede deshacer
    RESPUESTAS:
    • 200 OK: Estudiante eliminado correctamente
    • 404 Not Found: No existe estudiante con ese ID
    """
    # Intentar eliminar el estudiante
    success = eliminar_estudiante(session, estudiante_id)

    if not success:
        raise HTTPException(status_code=404, detail="Estudiante no encontrado")

    return {"message": "Estudiante eliminado correctamente"}


@app.post("/| MATERIA |/",
          response_model=Curso,
          status_code=status.HTTP_201_CREATED,
          tags=["| CURSOS |"])
def crear_curso(curso: Curso, session: Session = Depends(get_session)):

    try:
        return crear_curso(session, curso)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/| MATERIA |/",
         response_model=List[Curso],
         tags=["| CURSOS |"])

def listar_cursos(creditos: Optional[int] = None, codigo: Optional[str] = None, session: Session = Depends(get_session)):
    """
    LISTAR TODOS LOS CURSOS DISPONIBLES

    FILTROS DISPONIBLES:
    • creditos: Filtrar por número específico de créditos
    • codigo: Filtrar por código (búsqueda parcial)

    """
    return listar_cursos(session, creditos, codigo)


@app.get("/| MATERIA |/{curso_id}",
         response_model=Curso,
         tags=["| CURSOS |"])
def obtener_curso(curso_id: int, session: Session = Depends(get_session)):
    """
    OBTENER UN CURSO ESPECÍFICO POR SU ID
    """
    curso = obtener_curso(session, curso_id)
    if not curso:
        raise HTTPException(status_code=404, detail="Curso no encontrado")
    return curso


@app.get("/| MATERIA |/{curso_id}/estudiantes",
         response_model=Curso,
         tags=["| CURSOS |"])
def obtener_curso_con_estudiantes(curso_id: int, session: Session = Depends(get_session)):
    """
    OBTENER UN CURSO CON TODOS SUS ESTUDIANTES MATRICULADOS
    USO:
    • Ver la lista completa de estudiantes en un curso
    • Generar listas de asistencia
    • Consultar capacidad del curso
    """
    curso = obtener_curso_con_estudiantes(session, curso_id)
    if not curso:
        raise HTTPException(status_code=404, detail="Curso no encontrado")
    return curso


@app.put("/| MATERIA |/{curso_id}",
         response_model=Curso,
         tags=["| CURSOS |"])
def actualizar_curso(curso_id: int, curso_data: dict, session: Session = Depends(get_session)):
    """
    ACTUALIZAR LOS DATOS DE UN CURSO EXISTENTE
    """
    try:
        curso = actualizar_curso(session, curso_id, curso_data)
        if not curso:
            raise HTTPException(status_code=404, detail="Curso no encontrado")
        return curso
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.delete("/| MATERIA |/{curso_id}",
            tags=["| CURSOS |"])
def eliminar_curso(curso_id: int, session: Session = Depends(get_session)):
    """
    ELIMINAR UN CURSO DEL SISTEMA

    ADVERTENCIA:
    • Elimina también todas las matrículas asociadas
    • Los estudiantes pierden su matrícula en este curso
    """
    success = eliminar_curso(session, curso_id)
    if not success:
        raise HTTPException(status_code=404, detail="Curso no encontrado")
    return {"message": "Curso eliminado correctamente"}


@app.post("/| INSCRIPCION |/",
          tags=["| MATRICULAS |"])
def matricular_estudiante(estudiante_id: int, curso_id: int, session: Session = Depends(get_session)):
    """
    MATRICULAR UN ESTUDIANTE EN UN CURSO

    RESPUESTAS:
    • 200 OK: Matrícula exitosa
    • 404 Not Found: Estudiante o curso no existe
    • 409 Conflict: Ya está matriculado o hay conflicto de horario
    """
    try:
        success = matricular_estudiante(session, estudiante_id, curso_id)
        if not success:
            raise HTTPException(status_code=404, detail="Estudiante o curso no encontrado")
        return {"message": "Estudiante matriculado correctamente"}
    except ValueError as e:
        # 409 Conflict para violaciones de reglas de negocio
        raise HTTPException(status_code=409, detail=str(e))


@app.delete("/| INSCRIPCION |/",
            tags=["| MATRICULAS |"])
def desmatricular_estudiante(estudiante_id: int, curso_id: int, session: Session = Depends(get_session)):
    """
    DESMATRICULAR UN ESTUDIANTE DE UN CURSO

    PARÁMETROS:
    • estudiante_id: ID del estudiante a desmatricular
    • curso_id: ID del curso del que desmatricular

    """
    success = desmatricular_estudiante(session, estudiante_id, curso_id)
    if not success:
        raise HTTPException(status_code=404, detail="Matrícula no encontrada")
    return {"message": "Estudiante desmatriculado correctamente"}


@app.get("/| INSCRIPCION | /{estudiante_id}/cursos-lista",
         response_model=List[Curso],
         tags=["| MATRICULAS |"])
def cursos_de_estudiante(estudiante_id: int, session: Session = Depends(get_session)):
    """
    OBTENER LA LISTA DE CURSOS DE UN ESTUDIANTE

    DIFERENCIA CON EL ENDPOINT ANTERIOR:
    • Este endpoint retorna solo la lista de cursos (sin datos del estudiante)
    • Más eficiente cuando solo se necesitan los cursos
    """
    cursos = cursos_de_estudiante(session, estudiante_id)
    return cursos


@app.get("/| INSCRIPCION | /{curso_id}/estudiantes-lista",
         response_model=List[Estudiante],
         tags=["| MATRICULAS |"])
def estudiantes_de_curso(curso_id: int, session: Session = Depends(get_session)):
    """
    OBTENER LA LISTA DE ESTUDIANTES DE UN CURSO
    USOS:
    • Generar listas de clase
    • Consultar estudiantes por curso
    • Control de asistencia
    """
    estudiantes = estudiantes_de_curso(session, curso_id)
    return estudiantes


# ==================== 🏠 ENDPOINT RAIZ ====================

@app.get("/")
def root():

    return {
        "message": "Sistema de Gestión Universitaria",
        "docs": "/docs",    # Enlace a Swagger UI
        "redoc": "/redoc"   # Enlace a ReDoc
    }




if __name__ == "__main__":
    """
    PUNTO DE ENTRADA PARA EJECUCIÓN DIRECTA
    
    CUANDO SE EJECUTA:
    python main.py
    
    CONFIGURACIÓN DEL SERVIDOR:
    • host="0.0.0.0": Escucha en todas las interfaces
    • port=8000: Puerto por defecto para desarrollo
    
    """
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
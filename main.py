from fastapi import FastAPI, Depends, HTTPException, status
from sqlmodel import Session
from typing import List, Optional

from database import get_session, create_db_and_tables
from models import Estudiante, Curso
from crud import (
    crear_estudiante, listar_estudiantes, obtener_estudiante,
    actualizar_estudiante, eliminar_estudiante, obtener_estudiante_con_cursos,
    crear_curso, listar_cursos, obtener_curso, actualizar_curso,
    eliminar_curso, obtener_curso_con_estudiantes, matricular_estudiante,
    desmatricular_estudiante, cursos_de_estudiante, estudiantes_de_curso
)

app = FastAPI(
    title="Sistema de Gestión Universitaria",
    description="API para gestionar estudiantes, cursos y matrículas",
    version="1.0.0"
)

@app.on_event("startup")
def on_startup():
    create_db_and_tables()

# === ENDPOINTS PARA ESTUDIANTES ===

@app.post("/estudiantes/", response_model=Estudiante, status_code=status.HTTP_201_CREATED)
def crear_estudiante_endpoint(estudiante: Estudiante, session: Session = Depends(get_session)):
    """
    Crear un nuevo estudiante
    - **cedula**: Debe ser única (8-10 dígitos)
    - **nombre**: Nombre completo
    - **email**: Formato válido de email
    - **semestre**: Entre 1 y 12
    """
    try:
        return crear_estudiante(session, estudiante)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/estudiantes/", response_model=List[Estudiante])
def listar_estudiantes_endpoint(semestre: Optional[int] = None, session: Session = Depends(get_session)):
    """
    Listar todos los estudiantes
    - **semestre**: Filtrar por semestre (opcional)
    """
    return listar_estudiantes(session, semestre)

@app.get("/estudiantes/{estudiante_id}", response_model=Estudiante)
def obtener_estudiante_endpoint(estudiante_id: int, session: Session = Depends(get_session)):
    """
    Obtener un estudiante por ID
    """
    estudiante = obtener_estudiante(session, estudiante_id)
    if not estudiante:
        raise HTTPException(status_code=404, detail="Estudiante no encontrado")
    return estudiante

@app.get("/estudiantes/{estudiante_id}/cursos", response_model=Estudiante)
def obtener_estudiante_con_cursos_endpoint(estudiante_id: int, session: Session = Depends(get_session)):
    """
    Obtener un estudiante con sus cursos matriculados
    """
    estudiante = obtener_estudiante_con_cursos(session, estudiante_id)
    if not estudiante:
        raise HTTPException(status_code=404, detail="Estudiante no encontrado")
    return estudiante

@app.put("/estudiantes/{estudiante_id}", response_model=Estudiante)
def actualizar_estudiante_endpoint(estudiante_id: int, estudiante_data: dict, session: Session = Depends(get_session)):
    """
    Actualizar un estudiante
    """
    try:
        estudiante = actualizar_estudiante(session, estudiante_id, estudiante_data)
        if not estudiante:
            raise HTTPException(status_code=404, detail="Estudiante no encontrado")
        return estudiante
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.delete("/estudiantes/{estudiante_id}")
def eliminar_estudiante_endpoint(estudiante_id: int, session: Session = Depends(get_session)):
    """
    Eliminar un estudiante (elimina también sus matrículas)
    """
    success = eliminar_estudiante(session, estudiante_id)
    if not success:
        raise HTTPException(status_code=404, detail="Estudiante no encontrado")
    return {"message": "Estudiante eliminado correctamente"}

# === ENDPOINTS PARA CURSOS ===

@app.post("/cursos/", response_model=Curso, status_code=status.HTTP_201_CREATED)
def crear_curso_endpoint(curso: Curso, session: Session = Depends(get_session)):
    """
    Crear un nuevo curso
    - **codigo**: Debe ser único (formato AAA111)
    - **nombre**: Nombre del curso
    - **creditos**: Entre 1 y 6
    - **horario**: Horario del curso
    """
    try:
        return crear_curso(session, curso)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/cursos/", response_model=List[Curso])
def listar_cursos_endpoint(creditos: Optional[int] = None, codigo: Optional[str] = None, session: Session = Depends(get_session)):
    """
    Listar todos los cursos
    - **creditos**: Filtrar por créditos (opcional)
    - **codigo**: Filtrar por código (opcional)
    """
    return listar_cursos(session, creditos, codigo)

@app.get("/cursos/{curso_id}", response_model=Curso)
def obtener_curso_endpoint(curso_id: int, session: Session = Depends(get_session)):
    """
    Obtener un curso por ID
    """
    curso = obtener_curso(session, curso_id)
    if not curso:
        raise HTTPException(status_code=404, detail="Curso no encontrado")
    return curso

@app.get("/cursos/{curso_id}/estudiantes", response_model=Curso)
def obtener_curso_con_estudiantes_endpoint(curso_id: int, session: Session = Depends(get_session)):
    """
    Obtener un curso con sus estudiantes matriculados
    """
    curso = obtener_curso_con_estudiantes(session, curso_id)
    if not curso:
        raise HTTPException(status_code=404, detail="Curso no encontrado")
    return curso

@app.put("/cursos/{curso_id}", response_model=Curso)
def actualizar_curso_endpoint(curso_id: int, curso_data: dict, session: Session = Depends(get_session)):
    """
    Actualizar un curso
    """
    try:
        curso = actualizar_curso(session, curso_id, curso_data)
        if not curso:
            raise HTTPException(status_code=404, detail="Curso no encontrado")
        return curso
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.delete("/cursos/{curso_id}")
def eliminar_curso_endpoint(curso_id: int, session: Session = Depends(get_session)):
    """
    Eliminar un curso (elimina también las matrículas)
    """
    success = eliminar_curso(session, curso_id)
    if not success:
        raise HTTPException(status_code=404, detail="Curso no encontrado")
    return {"message": "Curso eliminado correctamente"}

# === ENDPOINTS DE MATRÍCULAS ===

@app.post("/matriculas/")
def matricular_estudiante_endpoint(estudiante_id: int, curso_id: int, session: Session = Depends(get_session)):
    """
    Matricular un estudiante en un curso
    - Verifica que no esté ya matriculado
    - Verifica conflictos de horario
    """
    try:
        success = matricular_estudiante(session, estudiante_id, curso_id)
        if not success:
            raise HTTPException(status_code=404, detail="Estudiante o curso no encontrado")
        return {"message": "Estudiante matriculado correctamente"}
    except ValueError as e:
        raise HTTPException(status_code=409, detail=str(e))

@app.delete("/matriculas/")
def desmatricular_estudiante_endpoint(estudiante_id: int, curso_id: int, session: Session = Depends(get_session)):
    """
    Desmatricular un estudiante de un curso
    """
    success = desmatricular_estudiante(session, estudiante_id, curso_id)
    if not success:
        raise HTTPException(status_code=404, detail="Matrícula no encontrada")
    return {"message": "Estudiante desmatriculado correctamente"}

@app.get("/estudiantes/{estudiante_id}/cursos-lista", response_model=List[Curso])
def cursos_de_estudiante_endpoint(estudiante_id: int, session: Session = Depends(get_session)):
    """
    Obtener la lista de cursos de un estudiante
    """
    cursos = cursos_de_estudiante(session, estudiante_id)
    return cursos

@app.get("/cursos/{curso_id}/estudiantes-lista", response_model=List[Estudiante])
def estudiantes_de_curso_endpoint(curso_id: int, session: Session = Depends(get_session)):
    """
    Obtener la lista de estudiantes de un curso
    """
    estudiantes = estudiantes_de_curso(session, curso_id)
    return estudiantes

@app.get("/")
def root():
    """
    Página de inicio
    """
    return {
        "message": "Sistema de Gestión Universitaria",
        "docs": "/docs",
        "redoc": "/redoc"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
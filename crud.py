from sqlmodel import Session, select, and_
from models import Estudiante, Curso, Matricula
from typing import List, Optional


# === OPERACIONES PARA ESTUDIANTES ===

def crear_estudiante(session: Session, estudiante: Estudiante) -> Estudiante:
    # Verificar cédula única
    existing = session.exec(
        select(Estudiante).where(Estudiante.cedula == estudiante.cedula)
    ).first()
    if existing:
        raise ValueError("Ya existe un estudiante con esta cédula")

    session.add(estudiante)
    session.commit()
    session.refresh(estudiante)
    return estudiante


def listar_estudiantes(session: Session, semestre: Optional[int] = None) -> List[Estudiante]:
    query = select(Estudiante)
    if semestre:
        query = query.where(Estudiante.semestre == semestre)
    return session.exec(query).all()


def obtener_estudiante(session: Session, estudiante_id: int) -> Optional[Estudiante]:
    return session.get(Estudiante, estudiante_id)


def obtener_estudiante_con_cursos(session: Session, estudiante_id: int) -> Optional[Estudiante]:
    estudiante = session.get(Estudiante, estudiante_id)
    if estudiante:
        # Forzar la carga de los cursos
        session.refresh(estudiante, attribute_names=["cursos"])
    return estudiante


def actualizar_estudiante(session: Session, estudiante_id: int, estudiante_data: dict) -> Optional[Estudiante]:
    estudiante = session.get(Estudiante, estudiante_id)
    if not estudiante:
        return None

    # Verificar cédula única si se está actualizando
    if 'cedula' in estudiante_data:
        existing = session.exec(
            select(Estudiante).where(
                and_(
                    Estudiante.cedula == estudiante_data['cedula'],
                    Estudiante.id != estudiante_id
                )
            )
        ).first()
        if existing:
            raise ValueError("Ya existe un estudiante con esta cédula")

    for key, value in estudiante_data.items():
        setattr(estudiante, key, value)

    session.commit()
    session.refresh(estudiante)
    return estudiante


def eliminar_estudiante(session: Session, estudiante_id: int) -> bool:
    estudiante = session.get(Estudiante, estudiante_id)
    if not estudiante:
        return False

    # Eliminación en cascada de las matrículas (gracias a la relación)
    session.delete(estudiante)
    session.commit()
    return True


# === OPERACIONES PARA CURSOS ===

def crear_curso(session: Session, curso: Curso) -> Curso:
    # Verificar código único
    existing = session.exec(
        select(Curso).where(Curso.codigo == curso.codigo)
    ).first()
    if existing:
        raise ValueError("Ya existe un curso con este código")

    session.add(curso)
    session.commit()
    session.refresh(curso)
    return curso


def listar_cursos(session: Session, creditos: Optional[int] = None, codigo: Optional[str] = None) -> List[Curso]:
    query = select(Curso)
    if creditos:
        query = query.where(Curso.creditos == creditos)
    if codigo:
        query = query.where(Curso.codigo.contains(codigo))
    return session.exec(query).all()


def obtener_curso(session: Session, curso_id: int) -> Optional[Curso]:
    return session.get(Curso, curso_id)


def obtener_curso_con_estudiantes(session: Session, curso_id: int) -> Optional[Curso]:
    curso = session.get(Curso, curso_id)
    if curso:
        session.refresh(curso, attribute_names=["estudiantes"])
    return curso


def actualizar_curso(session: Session, curso_id: int, curso_data: dict) -> Optional[Curso]:
    curso = session.get(Curso, curso_id)
    if not curso:
        return None

    # Verificar código único si se está actualizando
    if 'codigo' in curso_data:
        existing = session.exec(
            select(Curso).where(
                and_(
                    Curso.codigo == curso_data['codigo'],
                    Curso.id != curso_id
                )
            )
        ).first()
        if existing:
            raise ValueError("Ya existe un curso con este código")

    for key, value in curso_data.items():
        setattr(curso, key, value)

    session.commit()
    session.refresh(curso)
    return curso


def eliminar_curso(session: Session, curso_id: int) -> bool:
    curso = session.get(Curso, curso_id)
    if not curso:
        return False

    session.delete(curso)
    session.commit()
    return True


# === OPERACIONES DE MATRÍCULA ===

def matricular_estudiante(session: Session, estudiante_id: int, curso_id: int) -> bool:
    # Verificar que existan ambos
    estudiante = session.get(Estudiante, estudiante_id)
    curso = session.get(Curso, curso_id)
    if not estudiante or not curso:
        return False

    # Verificar que no esté ya matriculado (Lógica de negocio)
    existing = session.exec(
        select(Matricula).where(
            and_(
                Matricula.estudiante_id == estudiante_id,
                Matricula.curso_id == curso_id
            )
        )
    ).first()
    if existing:
        raise ValueError("El estudiante ya está matriculado en este curso")

    # Verificar que no tenga conflicto de horario (Lógica de negocio)
    cursos_matriculados = session.exec(
        select(Curso).join(Matricula).where(Matricula.estudiante_id == estudiante_id)
    ).all()

    nuevo_curso = session.get(Curso, curso_id)
    for curso_mat in cursos_matriculados:
        # Aquí podrías implementar una lógica más sofisticada de verificación de horarios
        if curso_mat.horario == nuevo_curso.horario:
            raise ValueError("El estudiante ya tiene un curso en este horario")

    # Crear matrícula
    matricula = Matricula(estudiante_id=estudiante_id, curso_id=curso_id)
    session.add(matricula)
    session.commit()
    return True


def desmatricular_estudiante(session: Session, estudiante_id: int, curso_id: int) -> bool:
    matricula = session.exec(
        select(Matricula).where(
            and_(
                Matricula.estudiante_id == estudiante_id,
                Matricula.curso_id == curso_id
            )
        )
    ).first()

    if not matricula:
        return False

    session.delete(matricula)
    session.commit()
    return True


def cursos_de_estudiante(session: Session, estudiante_id: int) -> List[Curso]:
    estudiante = session.get(Estudiante, estudiante_id)
    if not estudiante:
        return []

    session.refresh(estudiante, attribute_names=["cursos"])
    return estudiante.cursos


def estudiantes_de_curso(session: Session, curso_id: int) -> List[Estudiante]:
    curso = session.get(Curso, curso_id)
    if not curso:
        return []

    session.refresh(curso, attribute_names=["estudiantes"])
    return curso.estudiantes


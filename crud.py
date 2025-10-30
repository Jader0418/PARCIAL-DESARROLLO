"""
OPERACIONES CRUD - Create, Read, Update, Delete
Todas las operaciones de base de datos
"""
# Importar Session para operaciones de BD y select para consultas
from sqlmodel import Session, select, and_
# Importar tipos para tipado
from typing import List, Optional
from models import Estudiante, Curso, Matricula


def crear_estudiante(session: Session, estudiante: Estudiante) -> Estudiante:
    """
    CREAR nuevo estudiante con validación de cédula única
    """
    # VERIFICAR que no exista estudiante con misma cédula
    existing = session.exec(
        select(Estudiante).where(Estudiante.cedula == estudiante.cedula)
    ).first()

    #  Si existe, lanzar error
    if existing:
        raise ValueError("Ya existe un estudiante con esta cédula")

    # AÑADIR estudiante a la sesión
    session.add(estudiante)
    # GUARDAR cambios en la base de datos
    session.commit()
    # ACTUALIZAR objeto con datos de BD (ID automático, etc.)
    session.refresh(estudiante)
    return estudiante


def listar_estudiantes(session: Session, semestre: Optional[int] = None) -> List[Estudiante]:
    """
    LISTAR estudiantes con filtro opcional por semestre
    """
    # CREAR consulta base
    query = select(Estudiante)

    # SI se proporciona semestre, añadir filtro
    if semestre:
        query = query.where(Estudiante.semestre == semestre)

    # EJECUTAR consulta y devolver todos los resultados
    return session.exec(query).all()


def obtener_estudiante(session: Session, estudiante_id: int) -> Optional[Estudiante]:
    """
    OBTENER un estudiante por su ID
    """
    # BUSCAR estudiante por ID primario
    return session.get(Estudiante, estudiante_id)


def obtener_estudiante_con_cursos(session: Session, estudiante_id: int) -> Optional[Estudiante]:
    """
    OBTENER estudiante con sus cursos matriculados (CONSULTA RELACIONAL)
    """
    # BUSCAR estudiante por ID
    estudiante = session.get(Estudiante, estudiante_id)

    # SI existe, cargar relación de cursos
    if estudiante:
        session.refresh(estudiante, attribute_names=["cursos"])

    return estudiante


def actualizar_estudiante(session: Session, estudiante_id: int, estudiante_data: dict) -> Optional[Estudiante]:
    """
    ACTUALIZAR estudiante manteniendo validaciones
    """
    # 🔍 BUSCAR estudiante existente
    estudiante = session.get(Estudiante, estudiante_id)
    if not estudiante:
        return None

    #  SI se actualiza cédula, verificar que sea única
    if 'cedula' in estudiante_data:
        existing = session.exec(
            select(Estudiante).where(
                and_(
                    Estudiante.cedula == estudiante_data['cedula'],
                    Estudiante.id != estudiante_id  # Excluir el actual
                )
            )
        ).first()
        if existing:
            raise ValueError("Ya existe un estudiante con esta cédula")

    #  ACTUALIZAR campos del estudiante
    for key, value in estudiante_data.items():
        setattr(estudiante, key, value)

    # 💾 GUARDAR cambios
    session.commit()
    session.refresh(estudiante)
    return estudiante


def eliminar_estudiante(session: Session, estudiante_id: int) -> bool:
    """
    ELIMINAR estudiante (eliminación en cascada de matrículas)
    """
    # BUSCAR estudiante
    estudiante = session.get(Estudiante, estudiante_id)
    if not estudiante:
        return False

    # ELIMINAR estudiante (las matrículas se eliminan en cascada)
    session.delete(estudiante)
    session.commit()
    return True


def crear_curso(session: Session, curso: Curso) -> Curso:
    """
    CREAR nuevo curso con validación de código único
    """
    # VERIFICAR código único
    existing = session.exec(
        select(Curso).where(Curso.codigo == curso.codigo)
    ).first()
    if existing:
        raise ValueError("Ya existe un curso con este código")

    # AÑADIR curso
    session.add(curso)
    session.commit()
    session.refresh(curso)
    return curso


def listar_cursos(session: Session, creditos: Optional[int] = None, codigo: Optional[str] = None) -> List[Curso]:
    """
    LISTAR cursos con filtros opcionales
    """
    query = select(Curso)

    # FILTRO por créditos
    if creditos:
        query = query.where(Curso.creditos == creditos)

    # FILTRO por código (búsqueda parcial)
    if codigo:
        query = query.where(Curso.codigo.contains(codigo))

    return session.exec(query).all()


def obtener_curso(session: Session, curso_id: int) -> Optional[Curso]:
    """OBTENER curso por ID"""
    return session.get(Curso, curso_id)


def obtener_curso_con_estudiantes(session: Session, curso_id: int) -> Optional[Curso]:
    """
    OBTENER curso con sus estudiantes matriculados (CONSULTA RELACIONAL)
    """
    curso = session.get(Curso, curso_id)
    if curso:
        session.refresh(curso, attribute_names=["estudiantes"])
    return curso


def actualizar_curso(session: Session, curso_id: int, curso_data: dict) -> Optional[Curso]:
    """
    ACTUALIZAR curso manteniendo validaciones
    """
    curso = session.get(Curso, curso_id)
    if not curso:
        return None

    # VALIDAR código único si se actualiza
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

    # ACTUALIZAR campos
    for key, value in curso_data.items():
        setattr(curso, key, value)

    session.commit()
    session.refresh(curso)
    return curso


def eliminar_curso(session: Session, curso_id: int) -> bool:
    """ELIMINAR curso (eliminación en cascada)"""
    curso = session.get(Curso, curso_id)
    if not curso:
        return False

    session.delete(curso)
    session.commit()
    return True


def matricular_estudiante(session: Session, estudiante_id: int, curso_id: int) -> bool:
    """
    MATRICULAR estudiante en curso con validaciones de negocio
    """
    # VERIFICAR que existan estudiante y curso
    estudiante = session.get(Estudiante, estudiante_id)
    curso = session.get(Curso, curso_id)
    if not estudiante or not curso:
        return False

    # VALIDAR que no esté ya matriculado
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

    # VALIDAR conflictos de horario
    cursos_matriculados = session.exec(
        select(Curso).join(Matricula).where(Matricula.estudiante_id == estudiante_id)
    ).all()

    nuevo_curso = session.get(Curso, curso_id)
    for curso_mat in cursos_matriculados:
        # Validación simple: mismo horario = conflicto
        if curso_mat.horario == nuevo_curso.horario:
            raise ValueError("El estudiante ya tiene un curso en este horario")

    # CREAR matrícula
    matricula = Matricula(estudiante_id=estudiante_id, curso_id=curso_id)
    session.add(matricula)
    session.commit()
    return True


def desmatricular_estudiante(session: Session, estudiante_id: int, curso_id: int) -> bool:
    """
    DESMATRICULAR estudiante de curso
    """
    # 🔍 BUSCAR matrícula específica
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

    # ELIMINAR matrícula
    session.delete(matricula)
    session.commit()
    return True


def cursos_de_estudiante(session: Session, estudiante_id: int) -> List[Curso]:
    """
    OBTENER lista de cursos de un estudiante
    """
    estudiante = session.get(Estudiante, estudiante_id)
    if not estudiante:
        return []

    session.refresh(estudiante, attribute_names=["cursos"])
    return estudiante.cursos


def estudiantes_de_curso(session: Session, curso_id: int) -> List[Estudiante]:
    """
    OBTENER lista de estudiantes de un curso
    """
    curso = session.get(Curso, curso_id)
    if not curso:
        return []

    session.refresh(curso, attribute_names=["estudiantes"])
    return curso.estudiantes
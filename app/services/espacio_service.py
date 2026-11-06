from fastapi import HTTPException
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.models.espacio import Espacio
from app.schemas.espacio import EspacioCreate, EspacioUpdate

NOMBRE_DUPLICADO = "Ya existe un espacio académico con ese nombre"


def normalizar_nombre(nombre: str) -> str:
    return nombre.strip().casefold()


def _obtener_o_404(db: Session, espacio_id: int) -> Espacio:
    espacio = db.get(Espacio, espacio_id)
    if espacio is None:
        raise HTTPException(status_code=404, detail="Espacio académico no encontrado")
    return espacio


def _nombre_en_uso(db: Session, nombre_normalizado: str, excluir_id: int | None = None) -> bool:
    query = db.query(Espacio).filter(Espacio.nombre_normalizado == nombre_normalizado)
    if excluir_id is not None:
        query = query.filter(Espacio.id != excluir_id)
    return query.first() is not None


def _confirmar(db: Session, espacio: Espacio) -> Espacio:
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=409, detail=NOMBRE_DUPLICADO)
    db.refresh(espacio)
    return espacio


def crear_espacio(db: Session, datos: EspacioCreate) -> Espacio:
    nombre_normalizado = normalizar_nombre(datos.nombre)
    if _nombre_en_uso(db, nombre_normalizado):
        raise HTTPException(status_code=409, detail=NOMBRE_DUPLICADO)

    espacio = Espacio(
        nombre=datos.nombre,
        nombre_normalizado=nombre_normalizado,
        tipo=datos.tipo.value,
        capacidad=datos.capacidad,
        activo=True,
    )
    db.add(espacio)
    return _confirmar(db, espacio)


def listar_espacios(db: Session, incluir_inactivos: bool = False) -> list[Espacio]:
    query = db.query(Espacio)
    if not incluir_inactivos:
        query = query.filter(Espacio.activo.is_(True))
    return query.order_by(Espacio.id).all()


def obtener_espacio(db: Session, espacio_id: int) -> Espacio:
    return _obtener_o_404(db, espacio_id)


def actualizar_espacio(db: Session, espacio_id: int, datos: EspacioUpdate) -> Espacio:
    espacio = _obtener_o_404(db, espacio_id)
    nombre_normalizado = normalizar_nombre(datos.nombre)
    if _nombre_en_uso(db, nombre_normalizado, excluir_id=espacio_id):
        raise HTTPException(status_code=409, detail=NOMBRE_DUPLICADO)

    espacio.nombre = datos.nombre
    espacio.nombre_normalizado = nombre_normalizado
    espacio.tipo = datos.tipo.value
    espacio.capacidad = datos.capacidad
    return _confirmar(db, espacio)


def dar_de_baja_espacio(db: Session, espacio_id: int) -> Espacio:
    espacio = _obtener_o_404(db, espacio_id)
    if espacio.activo:
        espacio.activo = False
        _confirmar(db, espacio)
    return espacio

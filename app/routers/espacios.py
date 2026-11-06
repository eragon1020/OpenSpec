from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.espacio import EspacioCreate, EspacioRead, EspacioUpdate
from app.services import espacio_service

router = APIRouter(prefix="/espacios", tags=["espacios"])


@router.post("", response_model=EspacioRead, status_code=status.HTTP_201_CREATED)
def crear_espacio(datos: EspacioCreate, db: Session = Depends(get_db)) -> EspacioRead:
    return espacio_service.crear_espacio(db, datos)


@router.get("", response_model=list[EspacioRead])
def listar_espacios(
    incluir_inactivos: bool = Query(False),
    db: Session = Depends(get_db),
) -> list[EspacioRead]:
    return espacio_service.listar_espacios(db, incluir_inactivos=incluir_inactivos)


@router.get("/{espacio_id}", response_model=EspacioRead)
def obtener_espacio(espacio_id: int, db: Session = Depends(get_db)) -> EspacioRead:
    return espacio_service.obtener_espacio(db, espacio_id)


@router.put("/{espacio_id}", response_model=EspacioRead)
def actualizar_espacio(
    espacio_id: int,
    datos: EspacioUpdate,
    db: Session = Depends(get_db),
) -> EspacioRead:
    return espacio_service.actualizar_espacio(db, espacio_id, datos)


@router.delete("/{espacio_id}", status_code=status.HTTP_204_NO_CONTENT)
def dar_de_baja_espacio(espacio_id: int, db: Session = Depends(get_db)) -> None:
    espacio_service.dar_de_baja_espacio(db, espacio_id)

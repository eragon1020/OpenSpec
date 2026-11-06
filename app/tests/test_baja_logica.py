import pytest
from fastapi import HTTPException

from app.models.espacio import Espacio
from app.schemas.espacio import EspacioCreate
from app.services import espacio_service


def crear(db, nombre="Laboratorio de Física"):
    return espacio_service.crear_espacio(
        db,
        EspacioCreate(nombre=nombre, tipo="laboratorio", capacidad=30),
    )


def test_baja_logica_conserva_el_registro(db_session):
    espacio = crear(db_session)
    espacio_id = espacio.id

    dado_de_baja = espacio_service.dar_de_baja_espacio(db_session, espacio_id)

    assert dado_de_baja.activo is False
    assert db_session.get(Espacio, espacio_id) is not None
    assert db_session.query(Espacio).count() == 1


def test_baja_logica_es_idempotente(db_session):
    espacio = crear(db_session)
    espacio_id = espacio.id
    espacio_service.dar_de_baja_espacio(db_session, espacio_id)

    segunda_baja = espacio_service.dar_de_baja_espacio(db_session, espacio_id)

    assert segunda_baja.activo is False
    assert segunda_baja.nombre == "Laboratorio de Física"
    assert db_session.query(Espacio).count() == 1


def test_baja_logica_de_id_inexistente_devuelve_404(db_session):
    with pytest.raises(HTTPException) as exc:
        espacio_service.dar_de_baja_espacio(db_session, 9999)
    assert exc.value.status_code == 404

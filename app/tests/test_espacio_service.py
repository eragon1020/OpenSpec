import pytest
from fastapi import HTTPException

from app.models.espacio import Espacio
from app.schemas.espacio import EspacioCreate, EspacioUpdate
from app.services import espacio_service


def crear(db, nombre="Laboratorio de Física", tipo="laboratorio", capacidad=30):
    return espacio_service.crear_espacio(
        db,
        EspacioCreate(nombre=nombre, tipo=tipo, capacidad=capacidad),
    )


def test_crear_y_obtener_espacio(db_session):
    creado = crear(db_session)
    assert creado.id is not None
    assert creado.activo is True

    obtenido = espacio_service.obtener_espacio(db_session, creado.id)
    assert obtenido.nombre == "Laboratorio de Física"
    assert obtenido.tipo == "laboratorio"
    assert obtenido.capacidad == 30


def test_nombre_duplicado_ignora_mayusculas_y_espacios(db_session):
    crear(db_session)

    with pytest.raises(HTTPException) as exc:
        crear(db_session, nombre="  laboratorio de física  ")

    assert exc.value.status_code == 409
    assert db_session.query(Espacio).count() == 1


def test_edicion_con_nombre_de_otro_espacio_falla(db_session):
    primero = crear(db_session, nombre="Auditorio Principal", tipo="auditorio", capacidad=100)
    segundo = crear(db_session, nombre="Sala de Cómputo 1", tipo="sala_computo", capacidad=25)

    with pytest.raises(HTTPException) as exc:
        espacio_service.actualizar_espacio(
            db_session,
            segundo.id,
            EspacioUpdate(nombre=primero.nombre, tipo="sala_computo", capacidad=25),
        )

    assert exc.value.status_code == 409
    db_session.refresh(segundo)
    assert segundo.nombre == "Sala de Cómputo 1"


def test_consultar_id_inexistente_devuelve_404(db_session):
    with pytest.raises(HTTPException) as exc:
        espacio_service.obtener_espacio(db_session, 9999)
    assert exc.value.status_code == 404


def test_editar_espacio_existente(db_session):
    espacio = crear(db_session)

    actualizado = espacio_service.actualizar_espacio(
        db_session,
        espacio.id,
        EspacioUpdate(nombre="Laboratorio de Química", tipo="laboratorio", capacidad=40),
    )

    assert actualizado.nombre == "Laboratorio de Química"
    assert actualizado.capacidad == 40


def test_listado_por_defecto_solo_activos(db_session):
    activo = crear(db_session, nombre="Auditorio Principal", tipo="auditorio", capacidad=100)
    inactivo = crear(db_session, nombre="Sala de Cómputo 1", tipo="sala_computo", capacidad=25)
    espacio_service.dar_de_baja_espacio(db_session, inactivo.id)

    por_defecto = espacio_service.listar_espacios(db_session)
    con_inactivos = espacio_service.listar_espacios(db_session, incluir_inactivos=True)

    assert [e.id for e in por_defecto] == [activo.id]
    assert {e.id for e in con_inactivos} == {activo.id, inactivo.id}

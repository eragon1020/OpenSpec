import pytest
from pydantic import ValidationError

from app.schemas.espacio import EspacioCreate, EspacioRead


def test_creacion_valida_recorta_nombre():
    espacio = EspacioCreate(nombre="  Laboratorio de Física  ", tipo="laboratorio", capacidad=30)
    assert espacio.nombre == "Laboratorio de Física"
    assert espacio.tipo.value == "laboratorio"
    assert espacio.capacidad == 30


def test_rechaza_tipo_no_permitido():
    with pytest.raises(ValidationError):
        EspacioCreate(nombre="Sala", tipo="oficina", capacidad=10)


@pytest.mark.parametrize("capacidad", [0, -1])
def test_rechaza_capacidad_no_positiva(capacidad):
    with pytest.raises(ValidationError):
        EspacioCreate(nombre="Sala", tipo="auditorio", capacidad=capacidad)


@pytest.mark.parametrize("capacidad", [1.5, 10.0])
def test_rechaza_capacidad_decimal(capacidad):
    with pytest.raises(ValidationError):
        EspacioCreate(nombre="Sala", tipo="auditorio", capacidad=capacidad)


@pytest.mark.parametrize("nombre", ["", "   "])
def test_rechaza_nombre_vacio(nombre):
    with pytest.raises(ValidationError):
        EspacioCreate(nombre=nombre, tipo="laboratorio", capacidad=5)


@pytest.mark.parametrize("campo", ["nombre", "tipo", "capacidad"])
def test_rechaza_campos_ausentes(campo):
    datos = {"nombre": "Sala", "tipo": "laboratorio", "capacidad": 5}
    del datos[campo]
    with pytest.raises(ValidationError):
        EspacioCreate(**datos)


def test_read_incluye_estado():
    leido = EspacioRead(id=1, nombre="Sala", tipo="sala_computo", capacidad=20, activo=True)
    assert leido.activo is True

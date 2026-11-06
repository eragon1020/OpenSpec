import pytest

from app.models.espacio import Espacio


DATOS_VALIDOS = {"nombre": "Laboratorio de Física", "tipo": "laboratorio", "capacidad": 30}


def crear(client, **overrides):
    datos = {**DATOS_VALIDOS, **overrides}
    return client.post("/espacios", json=datos)


def test_crear_espacio_responde_201_con_estado_activo(client):
    respuesta = crear(client)

    assert respuesta.status_code == 201
    cuerpo = respuesta.json()
    assert cuerpo["id"] > 0
    assert cuerpo["nombre"] == "Laboratorio de Física"
    assert cuerpo["tipo"] == "laboratorio"
    assert cuerpo["capacidad"] == 30
    assert cuerpo["activo"] is True


@pytest.mark.parametrize("tipo", ["oficina", "LABORATORIO", ""])
def test_crear_tipo_no_permitido_responde_422(client, tipo):
    assert crear(client, tipo=tipo).status_code == 422


@pytest.mark.parametrize("capacidad", [0, -5, 1.5, "20"])
def test_crear_capacidad_invalida_responde_422(client, capacidad):
    assert crear(client, capacidad=capacidad).status_code == 422


def test_crear_nombre_duplicado_responde_409(client):
    assert crear(client).status_code == 201

    respuesta = crear(client, nombre="  laboratorio de física  ")

    assert respuesta.status_code == 409
    assert client.get("/espacios").json()[0]["nombre"] == "Laboratorio de Física"


@pytest.mark.parametrize(
    "datos",
    [
        {"tipo": "laboratorio", "capacidad": 30},
        {"nombre": "Sala", "capacidad": 30},
        {"nombre": "Sala", "tipo": "laboratorio"},
        {"nombre": "   ", "tipo": "laboratorio", "capacidad": 30},
    ],
)
def test_crear_campos_obligatorios_invalidos_responde_422(client, datos):
    assert client.post("/espacios", json=datos).status_code == 422



def test_ruta_post_aparece_en_openapi(client):
    esquema = client.get("/openapi.json").json()
    assert "post" in esquema["paths"]["/espacios"]


def test_listado_sin_espacios_devuelve_lista_vacia(client):
    respuesta = client.get("/espacios")
    assert respuesta.status_code == 200
    assert respuesta.json() == []


def test_listado_por_defecto_excluye_inactivos(client):
    activo = crear(client).json()
    inactivo = crear(client, nombre="Sala de Cómputo 1", tipo="sala_computo", capacidad=25).json()
    assert client.delete(f"/espacios/{inactivo['id']}").status_code == 204

    respuesta = client.get("/espacios")

    assert respuesta.status_code == 200
    assert [e["id"] for e in respuesta.json()] == [activo["id"]]


def test_listado_incluyendo_inactivos(client):
    activo = crear(client).json()
    inactivo = crear(client, nombre="Sala de Cómputo 1", tipo="sala_computo", capacidad=25).json()
    assert client.delete(f"/espacios/{inactivo['id']}").status_code == 204

    respuesta = client.get("/espacios", params={"incluir_inactivos": "true"})

    assert respuesta.status_code == 200
    por_id = {e["id"]: e for e in respuesta.json()}
    assert set(por_id) == {activo["id"], inactivo["id"]}
    assert por_id[activo["id"]]["activo"] is True
    assert por_id[inactivo["id"]]["activo"] is False


def test_listado_parametro_invalido_responde_422(client):
    assert client.get("/espacios", params={"incluir_inactivos": "no-es-booleano"}).status_code == 422


def test_consultar_espacio_activo(client):
    creado = crear(client).json()

    respuesta = client.get(f"/espacios/{creado['id']}")

    assert respuesta.status_code == 200
    assert respuesta.json() == creado


def test_consultar_espacio_inactivo(client):
    creado = crear(client).json()
    assert client.delete(f"/espacios/{creado['id']}").status_code == 204

    respuesta = client.get(f"/espacios/{creado['id']}")

    assert respuesta.status_code == 200
    cuerpo = respuesta.json()
    assert cuerpo["id"] == creado["id"]
    assert cuerpo["activo"] is False
    assert cuerpo["nombre"] == creado["nombre"]


def test_consultar_espacio_inexistente_responde_404(client):
    assert client.get("/espacios/9999").status_code == 404


def test_editar_espacio_existente(client):
    creado = crear(client).json()

    respuesta = client.put(
        f"/espacios/{creado['id']}",
        json={"nombre": "Laboratorio de Química", "tipo": "laboratorio", "capacidad": 40},
    )

    assert respuesta.status_code == 200
    cuerpo = respuesta.json()
    assert cuerpo["nombre"] == "Laboratorio de Química"
    assert cuerpo["capacidad"] == 40
    assert client.get(f"/espacios/{creado['id']}").json() == cuerpo


def test_editar_con_nombre_de_otro_espacio_responde_409(client):
    primero = crear(client).json()
    segundo = crear(client, nombre="Auditorio Principal", tipo="auditorio", capacidad=100).json()

    respuesta = client.put(
        f"/espacios/{segundo['id']}",
        json={"nombre": primero["nombre"], "tipo": "auditorio", "capacidad": 100},
    )

    assert respuesta.status_code == 409
    assert client.get(f"/espacios/{segundo['id']}").json()["nombre"] == "Auditorio Principal"


def test_editar_espacio_inexistente_responde_404(client):
    respuesta = client.put(
        "/espacios/9999",
        json={"nombre": "Sala", "tipo": "auditorio", "capacidad": 10},
    )
    assert respuesta.status_code == 404


@pytest.mark.parametrize(
    "datos",
    [
        {"nombre": "Sala", "tipo": "oficina", "capacidad": 10},
        {"nombre": "Sala", "tipo": "auditorio", "capacidad": 0},
        {"nombre": "", "tipo": "auditorio", "capacidad": 10},
        {"nombre": "Sala", "tipo": "auditorio"},
    ],
)
def test_editar_con_datos_invalidos_responde_422(client, datos):
    creado = crear(client).json()
    assert client.put(f"/espacios/{creado['id']}", json=datos).status_code == 422


def test_dar_de_baja_marca_inactivo_y_conserva_registro(client, db_session):
    creado = crear(client).json()

    respuesta = client.delete(f"/espacios/{creado['id']}")

    assert respuesta.status_code == 204
    assert respuesta.content == b""
    persistido = db_session.get(Espacio, creado["id"])
    assert persistido is not None
    assert persistido.activo is False


def test_dar_de_baja_es_idempotente(client, db_session):
    creado = crear(client).json()
    assert client.delete(f"/espacios/{creado['id']}").status_code == 204

    respuesta = client.delete(f"/espacios/{creado['id']}")

    assert respuesta.status_code == 204
    assert db_session.query(Espacio).filter(Espacio.id == creado["id"]).count() == 1
    assert db_session.get(Espacio, creado["id"]).activo is False


def test_dar_de_baja_espacio_inexistente_responde_404(client):
    assert client.delete("/espacios/9999").status_code == 404





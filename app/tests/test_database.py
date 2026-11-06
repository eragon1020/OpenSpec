from sqlalchemy import inspect


def test_fixture_crea_tabla_espacios(db_engine, client):
    assert inspect(db_engine).has_table("espacios")
    assert client.get("/openapi.json").status_code == 200

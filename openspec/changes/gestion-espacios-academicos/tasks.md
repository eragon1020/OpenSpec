# Tasks

## 1. Preparación del backend

- [ ] 1.1 Crear la estructura `app/` con `models/`, `schemas/`, `services/`, `routers/`, `tests/` y sus `__init__.py`; verificar con `find app -type f` que existen los directorios y archivos esperados.
- [ ] 1.2 Crear `requirements.txt` con FastAPI, Uvicorn, SQLAlchemy, Pydantic, pytest y httpx, instalar en un entorno virtual y verificar con `python -c "import fastapi, sqlalchemy, pydantic, pytest, httpx"` que no hay errores de importación.

## 2. Capa de datos

- [ ] 2.1 Implementar `app/database.py` con engine SQLite desde `DATABASE_URL` (default `sqlite:///./reservas.db`), `SessionLocal`, `Base` y la dependencia `get_db`; verificar que importar el módulo y ejecutar `Base.metadata.create_all(engine)` no produce errores.
- [ ] 2.2 Implementar el modelo `Espacio` en `app/models/espacio.py` con `id`, `nombre`, `nombre_normalizado` (índice único), `tipo` con CHECK de los tres valores, `capacidad` con CHECK > 0 y `activo` con default `true`; verificar con el inspector de SQLAlchemy que la tabla `espacios` existe con esas columnas y restricciones.
- [ ] 2.3 Configurar `app/tests/conftest.py` con engine SQLite en memoria (`StaticPool`), creación de tablas por prueba y override de `get_db` sobre `TestClient`; verificar con una prueba smoke que el fixture levanta la app y que el inspector ve la tabla `espacios`.

## 3. Esquemas y reglas de negocio

- [ ] 3.1 Implementar `app/schemas/espacio.py` con el enum `TipoEspacio` y los modelos `EspacioCreate`, `EspacioUpdate` y `EspacioRead`, incluyendo nombre no vacío y capacidad entera > 0; verificar con pruebas unitarias que rechazan tipo no permitido, capacidad 0/negativa/decimal y nombre vacío o ausente.
- [ ] 3.2 Implementar `app/services/espacio_service.py` con normalización `strip()` + `casefold()`, unicidad global (incluidos inactivos), creación, listado con filtro `activo`, consulta por id, y edición; verificar con pruebas de servicio que "Laboratorio de Física" y "  laboratorio de física  " colisionan como duplicados, que la edición duplicada falla y que consultar un id inexistente devuelve 404.
- [ ] 3.3 Implementar la baja lógica en el servicio (`activo = false`, sin borrado físico, idempotente); verificar con pruebas que tras la baja la fila sigue existiendo, que una segunda baja no altera el registro y que un id inexistente devuelve 404.

## 4. API REST

- [ ] 4.1 Crear `app/routers/espacios.py` con el endpoint `POST /espacios`, registrarlo en `app/main.py` y ejecutar `create_all` al arrancar; verificar con pruebas de API los casos 201 con estado activo, 422 por validación y 409 por nombre duplicado, y confirmar que la ruta aparece en `/openapi.json`.
- [ ] 4.2 Implementar `GET /espacios` con el query param `incluir_inactivos` (default `false`); verificar con pruebas que el listado por defecto excluye inactivos, que `incluir_inactivos=true` los devuelve y que sin registros responde 200 con lista vacía.
- [ ] 4.3 Implementar `GET /espacios/{id}` sin filtrar por estado; verificar con pruebas que devuelve activos e inactivos con su estado y que un id inexistente responde 404.
- [ ] 4.4 Implementar `PUT /espacios/{id}` para nombre, tipo y capacidad; verificar con pruebas la actualización exitosa, el conflicto 409 por nombre de otro espacio, el 404 por id inexistente y el 422 por datos inválidos.
- [ ] 4.5 Implementar `DELETE /espacios/{id}` como baja lógica idempotente; verificar con pruebas que un espacio activo pasa a inactivo con 204, que repetir la baja responde 204 sin cambios, que el registro permanece en la BD y que un id inexistente responde 404.
- [ ] 4.6 Documentar en `README.md` cómo instalar, arrancar y probar la API, junto con el contrato de `/espacios`; verificar que los comandos documentados se ejecutan tal cual y que los ejemplos de request/response coinciden con las pruebas de API.

## 5. Verificación de integración

- [ ] 5.1 Ejecutar la suite completa con `pytest app/tests -q` y verificar que todas las pruebas pasan y que cada escenario de `specs/espacios-academicos/spec.md` tiene al menos un test asociado por nombre.
- [ ] 5.2 Arrancar la API con Uvicorn y ejecutar el flujo manual crear → listar → consultar → editar → dar de baja → listar; verificar que el espacio dado de baja desaparece del listado por defecto, sigue consultable por id y permanece en la tabla `espacios`.

## Workflow follow-up

- Revisar el cambio completo contra la especificación y la propuesta antes de autorizar la implementación.
- Archivar el cambio cuando el proyecto cumpla sus requisitos de revisión y verificar el resultado archivado.

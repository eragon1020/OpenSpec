# Sistema de Gestión de Reservas — Módulo de Espacios Académicos

API REST para administrar el catálogo de espacios académicos (laboratorios, auditorios y salas de cómputo). Este repositorio contiene el primer módulo del sistema; las reservas y los usuarios se incorporarán en etapas posteriores.

## Requisitos

- Python 3.10 o superior (probado con 3.14).

## Instalación

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Ejecución

```bash
source .venv/bin/activate
uvicorn app.main:app --reload
```

La API queda disponible en `http://127.0.0.1:8000`, la documentación interactiva en `http://127.0.0.1:8000/docs` y el esquema OpenAPI en `http://127.0.0.1:8000/openapi.json`.

La base de datos SQLite se crea automáticamente al arrancar en `./reservas.db`. Puede cambiarse con la variable de entorno `DATABASE_URL`, por ejemplo:

```bash
DATABASE_URL=sqlite:///./mi_base.db uvicorn app.main:app
```

## Pruebas

```bash
source .venv/bin/activate
pytest app/tests -q
```

## Contrato de la API

Todas las rutas cuelgan de `/espacios`.

| Método | Ruta | Descripción | Éxito |
|---|---|---|---|
| `GET` | `/espacios?incluir_inactivos=false` | Lista espacios activos; con `incluir_inactivos=true` incluye también los inactivos | 200 |
| `GET` | `/espacios/{id}` | Consulta un espacio, esté activo o inactivo | 200 |
| `POST` | `/espacios` | Crea un espacio | 201 |
| `PUT` | `/espacios/{id}` | Reemplaza nombre, tipo y capacidad | 200 |
| `DELETE` | `/espacios/{id}` | Da de baja lógica el espacio (lo marca inactivo) | 204 |

Reglas:

- `nombre` es obligatorio, no vacío y único sin distinguir mayúsculas ni espacios exteriores.
- `tipo` debe ser `laboratorio`, `auditorio` o `sala_computo`.
- `capacidad` debe ser un entero mayor que cero.
- `DELETE` no borra físicamente: el espacio queda con `activo: false`, desaparece del listado por defecto y sigue consultable por `id`.
- Errores: `404` recurso no encontrado, `409` nombre duplicado, `422` datos inválidos. El cuerpo sigue el formato `{"detail": "..."}`.

### Crear un espacio

```bash
curl -X POST http://127.0.0.1:8000/espacios \
  -H "Content-Type: application/json" \
  -d '{"nombre": "Laboratorio de Física", "tipo": "laboratorio", "capacidad": 30}'
```

Respuesta `201`:

```json
{
  "id": 1,
  "nombre": "Laboratorio de Física",
  "tipo": "laboratorio",
  "capacidad": 30,
  "activo": true
}
```

### Listar espacios

```bash
curl http://127.0.0.1:8000/espacios
curl "http://127.0.0.1:8000/espacios?incluir_inactivos=true"
```

### Consultar, editar y dar de baja

```bash
curl http://127.0.0.1:8000/espacios/1

curl -X PUT http://127.0.0.1:8000/espacios/1 \
  -H "Content-Type: application/json" \
  -d '{"nombre": "Laboratorio de Química", "tipo": "laboratorio", "capacidad": 40}'

curl -X DELETE http://127.0.0.1:8000/espacios/1
```

Tras la baja, `GET /espacios/1` devuelve el espacio con `"activo": false` y `GET /espacios` ya no lo incluye.

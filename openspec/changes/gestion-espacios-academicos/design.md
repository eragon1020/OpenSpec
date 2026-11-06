# Design

## Context

Ver `proposal.md` para la motivación y `specs/espacios-academicos/spec.md` para los requisitos. El repositorio aún no contiene código de aplicación: este cambio crea el esqueleto del backend descrito en `PLAN_INGENIERIA.md` (FastAPI + SQLAlchemy + SQLite, arquitectura en capas `models → schemas → services → routers`). Por tanto, no hay esquema previo ni datos que migrar, pero el modelo de `espacios` quedará como base para los módulos posteriores de usuarios y reservas.

Restricciones relevantes:

- La baja debe ser lógica para que las reservas históricas sigan pudiendo referenciar el espacio.
- El nombre es único sin distinguir mayúsculas ni espacios exteriores; SQLite no ofrece unicidad case-insensitive nativa con soporte completo de Unicode.
- El listado por defecto solo muestra espacios activos, pero debe existir una vía explícita para consultar los inactivos.
- No hay autenticación ni autorización todavía (fuera de alcance).

## Goals / Non-Goals

**Goals:**

- Definir el modelo de datos de `espacios` con estado activo/inactivo y unicidad de nombre normalizada.
- Fijar el contrato REST (rutas, parámetros, códigos de estado y forma de los errores) que consumirán los módulos de reservas.
- Establecer la estructura de capas y la estrategia de pruebas que se reutilizará en módulos posteriores.
- Garantizar que la baja lógica sea idempotente y no rompa referencias futuras.

**Non-Goals:**

- Reactivación de espacios, edición del estado vía `PUT` o borrado físico.
- Paginación, búsqueda, filtros por tipo/capacidad u ordenamiento configurable del listado.
- Autenticación, autorización por roles, auditoría de cambios y migraciones con Alembic.
- Lógica de disponibilidad o reservas; solo se prepara el modelo para referenciarlo.

## Decisions

### 1. Persistencia: tabla `espacios` con baja lógica

Columnas:

| Columna | Tipo | Restricciones |
|---|---|---|
| `id` | Integer | PK, autoincremental |
| `nombre` | String(120) | NOT NULL, se guarda recortado |
| `nombre_normalizado` | String(120) | NOT NULL, UNIQUE (índice) |
| `tipo` | String(20) | NOT NULL, CHECK en `laboratorio`, `auditorio`, `sala_computo` |
| `capacidad` | Integer | NOT NULL, CHECK > 0 |
| `activo` | Boolean | NOT NULL, default `true` |

`nombre_normalizado` se calcula en el servicio con `strip()` + `casefold()` y es la clave de unicidad. Así se cumple la comparación sin distinguir mayúsculas y se cubren acentos (`Física` vs `física`), algo que `COLLATE NOCASE` de SQLite no resuelve por completo.

**Alternativas consideradas:**

- Índice único sobre `nombre COLLATE NOCASE`: más simple, pero solo pliega ASCII y fallaría con nombres acentuados.
- Consultar duplicados en aplicación sin restricción de BD: deja una ventana de carrera; se prefiere el índice único como red de seguridad.

La baja lógica (`activo = false`) sustituye al `DELETE` físico. Se conserva la fila y sus atributos, de modo que una futura FK `reservas.espacio_id` siga siendo válida.

### 2. Unicidad global, incluidos los espacios inactivos

El nombre de un espacio inactivo sigue reservado: no se permite crear ni renombrar otro espacio con ese nombre. Esto preserva la identidad histórica del espacio y evita que el historial de reservas apunte a un nombre ambiguo.

**Alternativa considerada:** liberar el nombre al dar de baja el espacio. Se descarta porque permitiría dos espacios distintos con el mismo nombre en el historial y complicaría la trazabilidad; además el spec no pide reutilización de nombres.

### 3. Contrato REST

| Método | Ruta | Éxito | Errores |
|---|---|---|---|
| `GET` | `/espacios?incluir_inactivos=false` | 200, lista | 422 si el parámetro no es booleano |
| `GET` | `/espacios/{id}` | 200, espacio (activo o inactivo) | 404 si no existe |
| `POST` | `/espacios` | 201, espacio creado | 422 validación, 409 nombre duplicado |
| `PUT` | `/espacios/{id}` | 200, espacio actualizado | 404, 422, 409 |
| `DELETE` | `/espacios/{id}` | 204 sin cuerpo | 404 si no existe |

Decisiones asociadas:

- `incluir_inactivos` es un query param booleano con default `false`; el listado por defecto filtra `activo = true`.
- `DELETE` marca `activo = false`. Si ya estaba inactivo responde igualmente `204` (idempotente) sin modificar la fila. Se elige `204` por convención REST y porque el cliente no necesita el cuerpo; **alternativa descartada:** `200` devolviendo el espacio, que añade payload sin aportar información nueva.
- `GET /espacios/{id}` no filtra por estado: los inactivos deben seguir siendo consultables para el historial.
- Los errores usan el formato estándar de FastAPI `{"detail": "..."}`. El 409 se lanza desde el servicio al detectar el índice único o una comprobación previa; el 404 cuando el `id` no existe. La validación de tipos, capacidad y campos obligatorios queda en los esquemas Pydantic (422).
- `PUT` actualiza solo `nombre`, `tipo` y `capacidad`; `activo` no es editable en este cambio.

### 4. Esquemas Pydantic separados por operación

- `EspacioCreate`: `nombre` (str no vacío, recortado), `tipo` (enum), `capacidad` (int > 0).
- `EspacioUpdate`: mismos campos, todos obligatorios en el cuerpo (semántica de reemplazo completa de los atributos editables). Si más adelante se requiere actualización parcial se añadirá `PATCH` en otro cambio.
- `EspacioRead`: `id`, `nombre`, `tipo`, `capacidad`, `activo`.
- `TipoEspacio` es un `Enum` de Python cuyos valores coinciden con los del CHECK de la BD, para que FastAPI devuelva 422 ante valores no permitidos y SQLAlchemy valide también en escritura.

La normalización del nombre y la comprobación de duplicados viven en `services`, no en los routers, para que la regla sea reutilizable y testeable sin HTTP.

### 5. Estructura y sesión de base de datos

Se respeta la organización del plan:

```
/app
  main.py            # instancia FastAPI, inclusión de routers, create_all
  database.py        # engine, SessionLocal, Base, get_db
  models/espacio.py
  schemas/espacio.py
  services/espacio_service.py
  routers/espacios.py
  tests/
```

- La ruta de la BD se toma de una variable de entorno (`DATABASE_URL`) con default `sqlite:///./reservas.db`.
- `get_db` como dependencia de FastAPI, cerrando la sesión en `finally`.
- Se usa `Base.metadata.create_all` al arrancar (no hay Alembic en este alcance). La creación de la tabla es idempotente.
- SQLite necesita `connect_args={"check_same_thread": False}` para FastAPI; en pruebas se usa una BD en memoria con `StaticPool` y override de `get_db`.

### 6. Estrategia de pruebas

- Fixtures de pytest que crean un engine SQLite en memoria por prueba, ejecutan `create_all`, sobreescriben `get_db` y usan `TestClient`.
- Un test de integración por escenario de aceptación del spec (creación válida, duplicado sin distinguir mayúsculas/espacios, tipo inválido, capacidad inválida, campos faltantes, listado por defecto e incluyendo inactivos, consulta de activo e inactivo, edición, conflicto de nombre, 404, baja lógica, baja idempotente y baja inexistente).
- El nombre de cada test se deriva del requisito (`test_baja_logica_*`, `test_listado_excluye_inactivos_*`) para conservar trazabilidad con el spec.

## Risks / Trade-offs

- **El nombre queda bloqueado tras la baja** → Se documenta como decisión; si el negocio pide reutilizar nombres, se resolverá en un cambio posterior con renombrado del espacio archivado.
- **`create_all` no gestiona evolución del esquema** → Aceptable en greenfield; cuando el esquema empiece a cambiar se introducirá Alembic. Mientras tanto, cualquier cambio destructivo en desarrollo se resuelve recreando la BD.
- **Normalización con `casefold()` puede sorprender en ciertos idiomas** → Es la opción estándar de Python para comparación case-insensitive y cubre los acentos esperados; se probará explícitamente con nombres acentuados.
- **Condiciones de carrera en la unicidad** → El índice único en `nombre_normalizado` garantiza el rechazo aunque dos peticiones pasen la comprobación previa; el servicio traduce la violación de integridad a 409.
- **Filas inactivas acumuladas** → Impacto bajo para el volumen previsto; el listado por defecto las excluye y no se prevé purga.
- **Sin autenticación, cualquiera puede dar de baja espacios** → Riesgo asumido y declarado fuera de alcance; el módulo de usuarios lo cubrirá después.

## Migration Plan

1. Crear el esqueleto del backend y las dependencias.
2. Al primer arranque, `create_all` crea la tabla `espacios`; no hay datos previos que migrar.
3. Verificar con la suite de pruebas y un arranque manual de la API.
4. Rollback: al ser greenfield, basta con revertir el cambio de código y eliminar el archivo SQLite generado; no existen consumidores ni datos en producción.

## Open Questions

- ¿Se necesitará reactivar espacios inactivos? El spec actual no lo contempla; si surge, se añadirá como nuevo requisito/endpoint sin alterar la baja lógica.
- ¿Se requerirá paginación o filtros en el listado cuando crezca el catálogo? Se puede añadir después manteniendo el contrato actual como subconjunto compatible.

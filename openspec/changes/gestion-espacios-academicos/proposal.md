# Proposal

## Why

La institución gestiona hoy los espacios académicos (laboratorios, auditorios y salas de cómputo) mediante correos y hojas de cálculo, lo que impide tener una fuente única de verdad sobre qué espacios existen, de qué tipo son y cuánta capacidad tienen. Sin ese catálogo centralizado no es posible construir después la validación de disponibilidad ni las reservas, por lo que este es el primer módulo del plan de ingeniería.

## What Changes

- Se introduce el catálogo de espacios académicos como primer módulo del sistema, con operaciones para crear, listar, consultar, editar y dar de baja espacios.
- Cada espacio tiene **nombre**, **tipo**, **capacidad** y un estado **activo/inactivo**, además de un identificador generado por el sistema.
- El tipo de espacio se restringe a un conjunto cerrado (`laboratorio`, `auditorio`, `sala_computo`) para evitar valores inconsistentes.
- Se define el contrato REST del módulo y sus reglas de validación (campos obligatorios, capacidad positiva, nombre no vacío y único).
- La baja de espacios es lógica: el espacio se marca como inactivo, deja de aparecer en el listado por defecto y se conserva para el historial de reservas.
- Se crea la base del proyecto backend (FastAPI + SQLAlchemy + SQLite) necesaria para ejecutar y probar este módulo.
- **Fuera de alcance:** reservas, disponibilidad, autenticación y autorización por roles (etapas posteriores del plan). El módulo se estructura para incorporar permisos cuando exista el módulo de usuarios, pero esta propuesta no los exige.

## Capabilities

### New Capabilities

- `espacios-academicos`: catálogo y administración de los espacios físicos de la institución (crear, listar, consultar, editar y dar de baja), incluyendo tipo, capacidad y estado.

### Modified Capabilities

- Ninguna.

## Impact

- **Código nuevo:** esqueleto del backend en `/app` (`models`, `schemas`, `services`, `routers`) y suite de pruebas en `/app/tests`; configuración de dependencias (FastAPI, SQLAlchemy, Pydantic, pytest) y de base de datos SQLite.
- **API:** nuevos endpoints REST bajo `/espacios` (`GET /espacios`, `GET /espacios/{id}`, `POST /espacios`, `PUT /espacios/{id}`, `DELETE /espacios/{id}` para la baja lógica).
- **Persistencia:** nueva tabla `espacios` (id, nombre, tipo, capacidad, estado).
- **Dependencias:** no se afectan módulos existentes porque el proyecto aún no contiene código de aplicación.
- **Riesgo principal:** fijar un contrato de tipos y validaciones que las etapas de reservas puedan consumir sin cambios incompatibles.

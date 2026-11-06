# espacios-academicos Specification

## Purpose

Mantener un catálogo centralizado de los espacios físicos de la institución (laboratorios, auditorios y salas de cómputo) con su tipo y capacidad, como base para la gestión posterior de reservas y disponibilidad.

## Requirements

### Requirement: Registro de espacios académicos

El sistema DEBE permitir crear un espacio académico con un nombre, un tipo y una capacidad. El nombre es obligatorio, no puede estar vacío ni repetirse (sin distinguir mayúsculas); el tipo DEBE ser uno de `laboratorio`, `auditorio` o `sala_computo`; la capacidad DEBE ser un entero mayor que cero. El sistema DEBE asignar un identificador único y devolver el espacio creado con todos sus atributos, incluyendo su estado como activo por defecto.

#### Scenario: Crear un espacio con datos válidos

- **WHEN** se envía una solicitud de creación con nombre "Laboratorio de Física", tipo `laboratorio` y capacidad 30
- **THEN** el sistema responde con código 201 y devuelve el espacio creado con un identificador único, su nombre, tipo, capacidad y estado activo
- **AND** el espacio queda disponible para consultas posteriores

#### Scenario: Rechazar un nombre duplicado

- **WHEN** se intenta crear un espacio con un nombre que ya existe, ignorando mayúsculas y espacios exteriores
- **THEN** el sistema rechaza la solicitud con un error de conflicto y no crea un nuevo espacio

#### Scenario: Rechazar un tipo de espacio no permitido

- **WHEN** se envía una solicitud de creación con un tipo distinto de `laboratorio`, `auditorio` o `sala_computo`
- **THEN** el sistema rechaza la solicitud con un error de validación y no crea el espacio

#### Scenario: Rechazar una capacidad no positiva o no entera

- **WHEN** se envía una solicitud de creación con capacidad 0, negativa o con decimales
- **THEN** el sistema rechaza la solicitud con un error de validación y no crea el espacio

#### Scenario: Rechazar campos obligatorios ausentes o vacíos

- **WHEN** se envía una solicitud de creación sin nombre, sin tipo o sin capacidad, o con el nombre vacío
- **THEN** el sistema rechaza la solicitud con un error de validación y no crea el espacio

### Requirement: Listado de espacios académicos

El sistema DEBE permitir obtener la lista de espacios académicos **activos**, incluyendo para cada uno su identificador, nombre, tipo, capacidad y estado. Los espacios inactivos NO DEBEN aparecer en el listado por defecto; el sistema DEBE ofrecer una forma explícita de solicitarlos cuando se requiera consultarlos (por ejemplo, para fines de historial). Cuando no existan espacios que cumplan el criterio, DEBE devolver una lista vacía.

#### Scenario: Listar espacios activos

- **WHEN** se solicita el listado de espacios por defecto y existen espacios activos e inactivos
- **THEN** el sistema responde con código 200 y devuelve únicamente los espacios activos con su identificador, nombre, tipo, capacidad y estado

#### Scenario: Listar incluyendo espacios inactivos

- **WHEN** se solicita el listado indicando explícitamente que incluya los espacios inactivos
- **THEN** el sistema responde con código 200 y devuelve tanto los espacios activos como los inactivos, con su identificador, nombre, tipo, capacidad y estado

#### Scenario: Listar sin espacios registrados

- **WHEN** se solicita el listado de espacios y no existe ninguno que cumpla el criterio
- **THEN** el sistema responde con código 200 y devuelve una lista vacía

### Requirement: Consulta de un espacio académico

El sistema DEBE permitir consultar un espacio académico por su identificador y devolver sus atributos, incluyendo su estado. Los espacios inactivos DEBEN seguir siendo consultables por identificador para conservar el historial de reservas. Si el identificador no corresponde a ningún espacio registrado, DEBE responder con un error de recurso no encontrado.

#### Scenario: Consultar un espacio activo existente

- **WHEN** se solicita un espacio activo por su identificador
- **THEN** el sistema responde con código 200 y devuelve el identificador, nombre, tipo, capacidad y estado de ese espacio

#### Scenario: Consultar un espacio inactivo

- **WHEN** se solicita por su identificador un espacio que fue dado de baja lógicamente
- **THEN** el sistema responde con código 200 y devuelve el identificador, nombre, tipo, capacidad y estado inactivo de ese espacio

#### Scenario: Consultar un espacio inexistente

- **WHEN** se solicita un espacio por un identificador que no está registrado
- **THEN** el sistema responde con un error de recurso no encontrado

### Requirement: Edición de espacios académicos

El sistema DEBE permitir modificar el nombre, el tipo y/o la capacidad de un espacio existente, aplicando las mismas reglas de validación y unicidad del registro. La edición DEBE rechazarse si el espacio no existe, y el nombre resultante no puede coincidir con el de otro espacio.

#### Scenario: Editar un espacio existente

- **WHEN** se envía una solicitud de edición con un nombre, tipo o capacidad válidos para un espacio registrado
- **THEN** el sistema responde con código 200 y devuelve el espacio con los atributos actualizados
- **AND** las consultas posteriores reflejan los nuevos valores

#### Scenario: Rechazar edición que duplica el nombre de otro espacio

- **WHEN** se intenta cambiar el nombre de un espacio a uno que ya pertenece a otro espacio
- **THEN** el sistema rechaza la solicitud con un error de conflicto y conserva los valores anteriores

#### Scenario: Rechazar la edición de un espacio inexistente

- **WHEN** se intenta editar un identificador que no corresponde a ningún espacio registrado
- **THEN** el sistema responde con un error de recurso no encontrado y no modifica ningún espacio

### Requirement: Baja lógica de espacios académicos

El sistema DEBE permitir dar de baja un espacio académico por su identificador mediante una baja lógica: el espacio DEBE marcarse como inactivo en lugar de eliminarse físicamente, conservando su registro y sus atributos para el historial de reservas. Tras la baja, el espacio NO DEBE aparecer en el listado por defecto, pero DEBE seguir siendo consultable por identificador. Si el identificador no corresponde a ningún espacio registrado, DEBE responder con un error de recurso no encontrado. La baja lógica DEBE ser idempotente: dar de baja un espacio ya inactivo DEBE confirmar la operación sin alterar el registro. La gestión de reservas asociadas queda fuera del alcance de este cambio.

#### Scenario: Dar de baja un espacio activo

- **WHEN** se solicita dar de baja un espacio activo por su identificador
- **THEN** el sistema marca el espacio como inactivo, lo conserva y responde confirmando la operación
- **AND** el espacio deja de aparecer en el listado por defecto
- **AND** la consulta posterior por su identificador devuelve el espacio con estado inactivo

#### Scenario: Dar de baja un espacio ya inactivo

- **WHEN** se solicita dar de baja un espacio que ya está inactivo
- **THEN** el sistema responde confirmando la operación sin modificaciones adicionales
- **AND** el registro del espacio se conserva

#### Scenario: Rechazar la baja de un espacio inexistente

- **WHEN** se solicita dar de baja un identificador que no corresponde a ningún espacio registrado
- **THEN** el sistema responde con un error de recurso no encontrado

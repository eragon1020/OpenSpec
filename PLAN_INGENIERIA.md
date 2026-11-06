# Plan de Ingeniería — Sistema de Gestión de Reservas de Espacios Académicos

## 1. Análisis del problema

### 1.1 Identificación de la problemática
La institución gestiona actualmente las reservas de espacios académicos (laboratorios, auditorios, salas de cómputo) mediante correos electrónicos y hojas de cálculo. Este proceso manual genera:
- Duplicidad de solicitudes para un mismo espacio y horario.
- Conflictos de horarios no detectados a tiempo.
- Dificultad para consultar la disponibilidad real de los espacios.
- Ausencia de trazabilidad sobre quién aprobó o rechazó una solicitud.

### 1.2 Necesidades de la institución
- Centralizar el registro de espacios y su disponibilidad.
- Permitir que los usuarios soliciten reservas sin depender de correos.
- Evitar reservas simultáneas sobre el mismo espacio y horario.
- Dar visibilidad del historial de reservas (aprobadas, rechazadas, canceladas).
- Soportar distintos niveles de permiso según el tipo de usuario.

### 1.3 Actores involucrados
- **Administrador**: gestiona los espacios académicos (alta, baja, edición) y los usuarios del sistema.
- **Solicitante** (docente/estudiante autorizado): crea, consulta y cancela sus propias solicitudes de reserva.
- **Aprobador** (coordinador de espacios): revisa, aprueba o rechaza las solicitudes de reserva.

### 1.4 Alcance y limitaciones del sistema
**Dentro del alcance:**
- Gestión de espacios académicos (laboratorios, auditorios, salas de cómputo).
- Registro y administración de usuarios con roles y permisos.
- Creación, validación, aprobación, rechazo y cancelación de solicitudes de reserva.
- Prevención de reservas simultáneas sobre el mismo espacio/horario.
- Historial de reservas por usuario y por espacio.

**Fuera del alcance (limitaciones):**
- Integración con sistemas externos de calendario institucional (Outlook, Google Calendar).
- Notificaciones por correo electrónico o push en tiempo real.
- Interfaz gráfica compleja tipo SPA; se prioriza una API funcional con una interfaz mínima de consumo.
- Soporte multi-sede o multi-institución.

## 2. Propuesta de solución

### 2.1 Descripción general
Un sistema backend tipo API REST que centraliza espacios, usuarios y reservas en una única fuente de verdad (base de datos SQLite), reemplazando el flujo manual de correos y hojas de cálculo. La validación de disponibilidad y la prevención de conflictos se ejecutan en el servidor antes de confirmar cualquier reserva.

### 2.2 Funcionalidades prioritarias
1. Gestión de espacios académicos (CRUD).
2. Registro y administración de usuarios con roles.
3. Creación de solicitudes de reserva.
4. Validación de disponibilidad y prevención de reservas simultáneas.
5. Aprobación/rechazo de solicitudes.
6. Cancelación e historial de reservas.

### 2.3 Organización del sistema en módulos
- `espacios`: catálogo y estado de los espacios académicos.
- `usuarios`: registro, roles y permisos.
- `reservas`: ciclo de vida de una solicitud (creación → validación → aprobación/rechazo → cancelación).
- `disponibilidad`: lógica de validación de cruces de horario (puede vivir dentro de `reservas` como servicio independiente para mantenerlo testeable por separado).

### 2.4 Estrategia de desarrollo progresivo
Se construye en capas horizontales dentro de cada módulo: primero el modelo de datos, luego las reglas de negocio, luego la exposición vía API. Los módulos se implementan en orden de dependencia (ver sección 4), nunca en paralelo, para mantener trazabilidad clara entre especificación e implementación.

## 3. Decisiones de arquitectura y tecnología

### 3.1 Arquitectura seleccionada
Arquitectura en capas (API → Servicios/Reglas de negocio → Acceso a datos), dentro de un monolito simple. Se justifica por el tamaño acotado del proyecto (un equipo de una persona, alcance académico) donde una arquitectura distribuida (microservicios) añadiría complejidad sin beneficio real.

### 3.2 Stack tecnológico propuesto
- **Lenguaje/Framework**: Python con FastAPI — permite definir la API de forma declarativa, genera documentación automática (OpenAPI/Swagger) que ayuda a verificar que la implementación corresponde a las especificaciones, y tiene curva de aprendizaje baja.
- **Persistencia**: SQLite — motor embebido, sin necesidad de servidor de base de datos separado, suficiente para el volumen esperado y para fines de evaluación académica.
- **ORM**: SQLAlchemy — para mantener el acceso a datos desacoplado de SQL crudo y facilitar pruebas con bases de datos en memoria.
- **Pruebas**: pytest.

### 3.3 Estrategia de persistencia de datos
Base de datos relacional única (SQLite) con tablas: `espacios`, `usuarios`, `roles`, `reservas`. Las reservas se validan contra solapamiento de horario mediante una consulta de rango de fechas antes de insertar; la integridad se refuerza con restricciones a nivel de aplicación (no solo de base de datos), porque SQLite tiene soporte limitado de constraints complejos.

### 3.4 Organización de componentes
```
/app
  /models      (entidades SQLAlchemy)
  /schemas     (validación de entrada/salida, Pydantic)
  /services    (reglas de negocio: disponibilidad, permisos)
  /routers     (endpoints FastAPI por módulo)
  /tests
```

### 3.5 Comparación de decisiones técnicas con alternativas descartadas

| Decisión | Alternativa descartada | Motivo del descarte |
|---|---|---|
| SQLite | PostgreSQL | Requiere levantar un servidor adicional; para el alcance y volumen del proyecto añade complejidad operativa sin beneficio medible. |
| FastAPI | Django (con DRF) | Django trae más convenciones y módulos (admin, ORM propio) que exceden lo necesario para una API acotada; FastAPI es más ligero y con mejor soporte nativo para documentación/validación automática. |
| Arquitectura en capas (monolito) | Microservicios | La separación en servicios independientes añadiría complejidad de despliegue y comunicación entre servicios que no se justifica para un sistema de un solo dominio y un solo desarrollador. |
| SQLAlchemy (ORM) | SQL crudo con sqlite3 | El SQL crudo complica las pruebas (fixtures, bases en memoria) y el mantenimiento al crecer el número de consultas; el ORM da una capa de abstracción más fácil de testear. |

## 4. Estrategia de desarrollo

### 4.1 Metodología de trabajo
Desarrollo incremental por módulo, siguiendo Spec-Driven Development: cada módulo pasa por especificación (OpenSpec) → revisión → implementación → pruebas, antes de iniciar el siguiente módulo.

### 4.2 Etapas de implementación y orden de desarrollo
1. **Espacios académicos** (no depende de nada más; es el catálogo base).
2. **Usuarios y roles/permisos** (independiente de espacios, pero necesario antes de reservas).
3. **Creación de solicitudes de reserva** (depende de 1 y 2).
4. **Validación de disponibilidad y prevención de reservas simultáneas** (depende de 3).
5. **Aprobación y rechazo de solicitudes** (depende de 3 y 4).
6. **Cancelación e historial de reservas** (depende de 5).

### 4.3 Dependencias entre componentes
`espacios` y `usuarios` son independientes entre sí. `reservas` depende de ambos. `disponibilidad` depende de `reservas`. `aprobación/rechazo` depende de que `disponibilidad` ya esté validando correctamente, para no aprobar solicitudes inválidas.

### 4.4 Criterios para considerar terminada cada etapa
Una etapa se considera terminada cuando: (a) su especificación en OpenSpec está revisada y sin contradicciones, (b) el código implementa todos los escenarios de aceptación definidos, (c) las pruebas automatizadas del módulo pasan, y (d) el commit correspondiente está registrado con referencia a la especificación que lo originó.

## 5. Estrategia de calidad

### 5.1 Tipos de pruebas
- **Pruebas unitarias**: lógica de validación de disponibilidad, reglas de permisos por rol.
- **Pruebas de integración**: endpoints de la API contra una base de datos SQLite en memoria (crear espacio → crear reserva → validar conflicto).
- **Pruebas de regresión**: re-ejecutar la suite completa tras el cambio de la regla de las 4 horas, para confirmar que no se rompió nada existente.

### 5.2 Riesgos identificados y mitigación

| # | Riesgo | Mitigación |
|---|---|---|
| 1 | La IA genera código que no corresponde a la especificación | Revisar manualmente cada entrega del agente contra el escenario de aceptación antes de aceptar el commit. |
| 2 | Condiciones de carrera al validar disponibilidad (dos solicitudes casi simultáneas para el mismo espacio) | Usar una transacción con verificación de solapamiento antes del insert, y una restricción a nivel de aplicación que rechace la segunda si ya existe una reserva aprobada en el rango. |
| 3 | Especificaciones ambiguas que lleven a una implementación incorrecta | Revisión explícita de cada spec (Fase 2 de OpenSpec) antes de autorizar implementación. |
| 4 | El cambio de negocio (máx. 4 horas) rompe reservas/pruebas existentes | Actualizar primero la especificación, definir el nuevo escenario de aceptación, y correr toda la suite de regresión antes de cerrar el cambio. |
| 5 | Pérdida de trazabilidad entre plan, specs y código por mezclar commits | Disciplina de commits atómicos: un commit = una especificación o una tarea de implementación, nunca una mezcla de etapas. |

### 5.3 Mecanismos de verificación de requisitos
Cada requisito de OpenSpec se traduce en al menos un caso de prueba automatizado con nombre trazable al requisito (ej. `test_no_permite_reserva_simultanea`). La cobertura de pruebas por módulo se revisa antes de marcar la etapa como cerrada.

## 6. Uso de SDD e inteligencia artificial

### 6.1 Uso de OpenSpec
OpenSpec se usará para formalizar cada módulo priorizado en este plan como una propuesta con requisitos y escenarios "Given/When/Then" verificables, antes de escribir una sola línea de código de ese módulo.

### 6.2 Transformación del plan en especificaciones
Cada funcionalidad prioritaria (sección 2.2) se convierte en una propuesta de OpenSpec independiente, heredando los actores (sección 1.3) y las restricciones de alcance (sección 1.4) ya definidas aquí.

### 6.3 Actividades delegadas a la IA
- Redacción inicial de especificaciones a partir de los requisitos de este plan (revisadas por el estudiante).
- Generación de código de cada módulo a partir de su especificación ya revisada.
- Generación de pruebas automatizadas a partir de los escenarios de aceptación.

### 6.4 Verificación del código generado
Cada entrega de la IA se revisa manualmente contra: (a) la especificación que la originó, (b) la arquitectura en capas definida en la sección 3, y (c) el resultado de ejecutar la suite de pruebas correspondiente.

### 6.5 Decisiones responsabilidad del estudiante
La arquitectura, el stack tecnológico, la organización en módulos, el orden de desarrollo, la aceptación o rechazo de cada especificación, y la decisión final de si una implementación generada por IA es correcta y se integra al proyecto.

# Incidencias IA: clasificación y priorización de incidencias con IA

## 1. Qué es

Proyecto final del seminario: módulo de un sistema web de inventarios en el que la IA sugiere la
prioridad de cada incidencia y el técnico de soporte toma la decisión final. Este incremento
implementa **HU-03: ajuste manual de prioridad por el técnico, con justificación cuando corresponda**,
con registro de auditoría de cada cambio. Por ahora la persistencia es un repositorio en memoria.

La revisión de código y de seguridad está en [`revision_seguridad.md`](revision_seguridad.md).

#### Historia de usuario

**HU-03. Ajuste manual de prioridad por el técnico, con justificación cuando corresponda.**

> Como técnico de soporte quiero corregir la prioridad que sugirió la IA para que la
> decisión final sea humana y quede trazable.

**Criterio de aceptación (HU-03)**

```gherkin
Escenario: Corrección de la prioridad sugerida
  Dado un ticket abierto con prioridad sugerida "Media" y prioridad vigente "Media"
  Cuando el técnico de soporte cambia la prioridad a "Alta" con la justificación "Afecta el cierre de caja"
  Entonces la prioridad vigente del ticket es "Alta"
  Y la prioridad sugerida por la IA sigue siendo "Media"
  Y se guarda un registro de auditoría con usuario, fecha, prioridad anterior, sugerida, final y justificación

Escenario: Cambio rechazado
  Dado un ticket y un cambio que no cumple las reglas (prioridad inválida, falta justificación,
       ticket inexistente o cerrado, o usuario que no es técnico)
  Cuando el técnico intenta cambiar la prioridad
  Entonces el sistema rechaza el cambio con un error
  Y no cambia la prioridad ni crea registro de auditoría
```

Fuente en el diseño S4: sección 5 (entidades `Ticket` e `HistorialPrioridad`) y sección 6
(`PATCH /api/tickets/{id}/prioridad`, historia HU-03).

#### Contrato de la función

```python
def cambiar_prioridad(
    repositorio,                      # objeto con obtener_ticket() y guardar_cambio_prioridad()
    ticket_id: int,
    nueva_prioridad: str,             # "Baja" | "Media" | "Alta" | "Crítica" (distingue mayúsculas)
    usuario: Usuario,                 # quien hace el cambio; debe tener rol "soporte"
    justificacion: str | None = None,
    *,
    ahora: datetime | None = None,    # solo por nombre y con zona horaria; por defecto, ahora en UTC
) -> RegistroAuditoria
```

**Qué recibe.** El repositorio, el id del ticket, la nueva prioridad, el usuario y, opcionalmente,
una justificación.

**Qué devuelve.** El `RegistroAuditoria` creado, con `ticket_id`, `usuario_id`,
`prioridad_anterior`, `prioridad_sugerida`, `prioridad_final`, `justificacion` y `fecha_cambio`.
Como efecto, actualiza `prioridad_actual` del ticket y guarda el registro, las dos cosas juntas.
Nunca modifica `prioridad_sugerida`.

**Reglas y casos límite**

- Solo el rol `soporte` puede cambiar la prioridad.
- La justificación es obligatoria cuando `nueva_prioridad` es distinta de `prioridad_sugerida`.
  Si el ticket aún no tiene sugerencia (análisis pendiente por timeout o error de la IA), siempre se exige.
  Si la nueva prioridad coincide con la sugerida, es opcional.
- Una justificación de solo espacios cuenta como ausente. Se guarda sin espacios al inicio ni al final.
- Un ticket cerrado no admite cambios. Pedir la prioridad que el ticket ya tiene tampoco.
- La justificación admite hasta 500 caracteres, sin saltos de línea ni caracteres de control.
- Un error nunca deja cambios parciales: ni prioridad modificada ni registro de auditoría.

**Errores**

| Situación | Error | Código HTTP de la API |
|---|---|---|
| Prioridad fuera de la lista (incluye `None`, vacío o distinta capitalización) | `PrioridadInvalidaError` | 400 |
| Falta la justificación exigida | `JustificacionRequeridaError` | 400 |
| Justificación que no es texto, de más de 500 caracteres o con saltos de línea o caracteres de control | `JustificacionInvalidaError` | 400 |
| El usuario no es técnico | `PermisoDenegadoError` | 403 |
| El ticket no existe | `TicketNoEncontradoError` | 404 |
| Ticket cerrado, o prioridad igual a la vigente | `ConflictoError` | 409 |

**Ejemplos de entrada y salida**

| # | Estado del ticket | Llamada | Resultado |
|---|---|---|---|
| 1 | sugerida `Media`, vigente `Media`, abierto | `cambiar_prioridad(repo, 1, "Alta", tecnico, "Afecta el cierre de caja")` | Registro con anterior `Media`, final `Alta`; vigente `Alta`, sugerida `Media` |
| 2 | sugerida `Media`, vigente `Baja`, abierto | `cambiar_prioridad(repo, 1, "Media", tecnico)` | Registro con justificación `None` (coincide con la sugerida) |
| 3 | sugerida `None`, vigente `None`, pendiente | `cambiar_prioridad(repo, 1, "Alta", tecnico)` | `JustificacionRequeridaError` (400) |
| 4 | cualquiera | `cambiar_prioridad(repo, 1, "Urgente", tecnico, "x")` | `PrioridadInvalidaError` (400) |
| 5 | ticket 999 inexistente | `cambiar_prioridad(repo, 999, "Alta", tecnico, "x")` | `TicketNoEncontradoError` (404) |

#### Supuestos (el documento de diseño no los define)

- Niveles de prioridad: `Baja`, `Media`, `Alta` y `Crítica`. `Crítica` sale de la HU-04 del documento de requisitos ([`docs/requisitos.pdf`](docs/requisitos.pdf)); la primera versión del código solo tenía tres niveles.
- Estados del ticket: `abierto`, `pendiente_clasificacion` y `cerrado` (exactos; otro valor da `ValueError`).
- Longitud máxima de la justificación: 500 caracteres.
- «Justificación cuando corresponda» se interpreta como la regla de arriba (obligatoria si se aparta de la IA).
- El código 403 no aparece en la tabla de la API del diseño; se agrega para el caso de un usuario sin rol de técnico.
- El repositorio es en memoria. Sustituirlo por la base de datos real queda para un incremento posterior.

## 2. Requisitos

- Python 3.10 o superior (probado con 3.13).
- Git.
- El código usa solo la biblioteca estándar. Para el linter, las pruebas con pytest y la auditoría
  de dependencias se usan ruff, pytest y pip-audit, con versión fijada en `pyproject.toml`
  (`[project.optional-dependencies] dev`).

## 3. Instalación

```bash
git clone https://github.com/AndrexxR/Proyecto-Final-Seminario.git
```

```bash
cd Proyecto-Final-Seminario
```

```bash
python -m venv .venv
```

Activa el entorno: `source .venv/bin/activate` en Linux o macOS, `.venv\Scripts\activate` en Windows.

```bash
pip install ruff==0.16.9 pytest==9.2.0 pip-audit==2.10.1
```

Si vas a configurar la base de datos o el servicio de IA (próximos incrementos), copia `.env.example`
como `.env` y pon tus valores. `.env` no se sube al repositorio.

## 4. Ejecución

Demostración por consola de HU-03: recorre los ejemplos del contrato (cambio correcto, 403, 400, 404
y vuelta a la sugerencia de la IA) y muestra el resultado de cada uno.

```bash
python -m incidencias
```

Salida esperada:

```text
OK    Técnico sube a Alta con justificación: Media -> Alta (justificación: 'Afecta el cierre de caja')
403   Operativo intenta cambiarla: Solo el técnico de soporte puede cambiar la prioridad
400   Técnico pide una prioridad que no existe: Prioridad inválida: 'Urgente'
404   Técnico cambia un ticket que no existe: No existe el ticket 999
OK    Técnico vuelve a la sugerencia de la IA: Alta -> Media (justificación: None)

Registros de auditoría guardados: 2
```

## 5. Pruebas

Toda la suite: pruebas de HU-03 (`test_prioridad.py`), de seguridad y abuso (`test_seguridad.py`),
de las reglas con particiones, límites y tabla de decisión (`test_reglas.py`) y con datos sintéticos
(`test_con_datos.py`). El diseño de los casos está en [`registro_pruebas.md`](registro_pruebas.md).

```bash
python -m pytest -v
```

Linter (reglas E, F, B y S, configuradas en `pyproject.toml`) y auditoría de las dependencias
instaladas en el entorno virtual:

```bash
ruff check .
```

```bash
pip-audit
```

## 6. Estructura

```
incidencias/modelos.py       Ticket, Usuario, RegistroAuditoria, constantes y errores
incidencias/prioridad.py     cambiar_prioridad (HU-03) y sus validaciones
incidencias/repositorio.py   Repositorio en memoria (reemplaza a la BD y a la auditoría)
incidencias/__main__.py      Demostración por consola (python -m incidencias)
tests/test_prioridad.py      Pruebas de HU-03: normales, límite y error
tests/test_seguridad.py      Pruebas de los hallazgos corregidos y de abuso
tests/test_reglas.py         Pruebas de las reglas: particiones, límites y tabla de decisión
tests/test_con_datos.py      Pruebas con los datos sintéticos
tests/conftest.py            Fixtures que cargan los datos sintéticos
tests/datos/                 Datos sintéticos de usuarios, tickets y justificaciones
registro_pruebas.md          Reglas, tablas de casos, revisión de las pruebas y errores introducidos
docs/revision_ia.md          Prompt y respuesta de la revisión con IA, con su verificación
revision_seguridad.md        Informe de revisión de código y seguridad
bitacora_ia.md               Bitácora de uso de IA
pyproject.toml               Metadatos, dependencias de desarrollo fijadas y configuración de ruff y pytest
.env.example                 Variables de entorno de ejemplo (sin valores reales)
```

## 7. Uso de IA

Usé Claude como asistente en todo el proyecto: para pasar del diseño S4 al contrato y a las pruebas,
para la segunda revisión de código, como agente de código para las correcciones (en una rama propia,
`claude/wonderful-cerf-d5iioc`, cuyo diff revisé antes de integrarla) y para proponer casos, pruebas y
datos sintéticos, que revisé contra las reglas en [`registro_pruebas.md`](registro_pruebas.md). Cada sugerencia está en [`bitacora_ia.md`](bitacora_ia.md) con la decisión (aceptada,
con cambios o rechazada), el motivo y cómo la verifiqué. Cada hallazgo de la IA lo reproduje en el
código antes de aceptarlo ([`docs/revision_ia.md`](docs/revision_ia.md)); los falsos positivos están
en el informe de seguridad.

## 8. Autor y licencia

- **Autor:** Carlos Andrés Rueda. Seminario, proyecto final, 2026.
- **Licencia:** MIT.

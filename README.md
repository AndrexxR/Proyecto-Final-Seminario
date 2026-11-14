# Sistema web de inventarios: clasificación y priorización de incidencias con IA

Proyecto final del seminario. Este repositorio contiene la primera funcionalidad
construida con pruebas primero y con un asistente de código (ver `bitacora_ia.md`).

## Funcionalidad de la semana 5

### Historia de usuario

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

### Contrato de la función

```python
def cambiar_prioridad(
    repositorio,                      # objeto con obtener_ticket() y guardar_cambio_prioridad()
    ticket_id: int,
    nueva_prioridad: str,             # "Baja" | "Media" | "Alta" (distingue mayúsculas)
    usuario: Usuario,                 # quien hace el cambio; debe tener rol "soporte"
    justificacion: str | None = None,
    ahora: datetime | None = None,    # solo para pruebas; por defecto, la hora actual en UTC
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
- Un error nunca deja cambios parciales: ni prioridad modificada ni registro de auditoría.

**Errores**

| Situación | Error | Código HTTP de la API |
|---|---|---|
| Prioridad fuera de la lista (incluye `None`, vacío o distinta capitalización) | `PrioridadInvalidaError` | 400 |
| Falta la justificación exigida | `JustificacionRequeridaError` | 400 |
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

### Supuestos (el documento de diseño no los define)

- Niveles de prioridad: `Baja`, `Media`, `Alta`. El diseño solo muestra `Alta` como ejemplo.
- Estados del ticket: se usan `abierto`, `pendiente_clasificacion` y `cerrado`.
- «Justificación cuando corresponda» se interpreta como la regla de arriba (obligatoria si se aparta de la IA).
- El código 403 no aparece en la tabla de la API del diseño; se agrega para el caso de un usuario sin rol de técnico.
- El repositorio es en memoria. Sustituirlo por la base de datos real es trabajo de otra semana.

### Cómo ejecutar las pruebas

Solo se usa la biblioteca estándar de Python 3.10 o superior (no hay dependencias que instalar):

```bash
python -m unittest        # desde la raíz del repositorio
```

Las pruebas están escritas con `unittest`, así que `pytest` también las ejecuta:

```bash
pytest
```

### Estructura

```
incidencias/modelos.py       Ticket, Usuario, RegistroAuditoria y errores
incidencias/repositorio.py   Repositorio en memoria (stand-in de la BD y la auditoría)
incidencias/prioridad.py     cambiar_prioridad (HU-03)
tests/test_prioridad.py      Pruebas: normales, límite y error
bitacora_ia.md               Bitácora de uso de IA
```

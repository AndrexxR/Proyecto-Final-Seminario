# Revisión de código con IA

- **Fecha:** 2026-11-14
- **Asistente:** Claude (Claude Code, sesión en la nube), trabajando en la rama `claude/wonderful-cerf-d5iioc`.
- **Commit revisado:** `0a04fa6` (código de HU-03 antes de las correcciones).
- **Alcance:** `incidencias/modelos.py`, `incidencias/prioridad.py`, `incidencias/repositorio.py`.

## Prompt usado

> Actúa como revisor de código senior con foco en seguridad. Revisa los archivos `incidencias/modelos.py`,
> `incidencias/prioridad.py` e `incidencias/repositorio.py` (Python 3.10+, solo biblioteca estándar).
> Contexto: implementan HU-03, el técnico de soporte cambia la prioridad sugerida por la IA y queda un
> registro de auditoría; el contrato está en el README.
> Criterios: (1) corrección y pruebas, (2) diseño y legibilidad (nombres, valores mágicos, duplicación,
> funciones largas), (3) seguridad: inyección, secretos, contraseñas, control de acceso, validación de
> entradas, integridad de la auditoría.
> Devuelve una tabla con: id, archivo y línea, problema, categoría OWASP o tipo, severidad (alta, media,
> baja) y corrección sugerida. Separa en dos tablas los **problemas seguros** (los puedes demostrar con una
> entrada concreta) de las **sospechas** (dependen de cómo se use el código). No inventes líneas: si no
> estás seguro, ponlo en sospechas.

## Respuesta de la IA (resumida, sin editar los hallazgos)

### Problemas seguros

| Id | Archivo y línea | Problema | Categoría | Severidad | Corrección sugerida |
|---|---|---|---|---|---|
| IA-01 | prioridad.py:58 | Si `justificacion` no es texto (por ejemplo, un número llegado del JSON), `.strip()` lanza `AttributeError`: error 500 en lugar de 400 | A04 Diseño inseguro / validación de entrada | Media | Validar el tipo y lanzar un error de dominio 400 |
| IA-02 | prioridad.py:58 | La justificación no tiene longitud máxima: se puede guardar 1 MB o más en la auditoría | A04 / consumo de recursos | Media | Límite de longitud con constante y error 400 |
| IA-03 | prioridad.py:58 | La justificación acepta saltos de línea y caracteres de control: permite falsificar líneas en registros de auditoría o logs | A09 Fallas de registro (inyección en logs) | Baja | Rechazar caracteres de control |
| IA-04 | repositorio.py:10-11 | `obtener_ticket` devuelve el objeto interno: quien lo reciba puede cambiar `prioridad_actual` sin pasar por `cambiar_prioridad` ni dejar auditoría | A01 Control de acceso / integridad | Media | Devolver una copia y guardar copias |
| IA-10 | modelos.py:9, prioridad.py:39 | `estado` es texto libre: `"Cerrado"` o `" cerrado"` no se reconocen como cerrado y el ticket acepta cambios | A04 / valor mágico | Media | Lista de estados válidos y validación al crear el `Ticket` |

### Sospechas

| Id | Archivo y línea | Sospecha | Categoría | Severidad | Corrección sugerida |
|---|---|---|---|---|---|
| IA-05 | prioridad.py:29 | Si `usuario` es `None`, `usuario.rol` lanza `AttributeError` | Validación de entrada | Baja | Comprobar `usuario is None` y lanzar 403 |
| IA-06 | prioridad.py:32 | El mensaje de error incluye el valor enviado por el usuario: posible XSS si se muestra en HTML | A03 Inyección (XSS reflejado) | Baja | No incluir la entrada en el mensaje |
| IA-07 | prioridad.py:56-73 | Leer y guardar no es atómico: dos técnicos a la vez pueden perder un cambio (condición de carrera) | A04 / concurrencia | Media | Transacción con bloqueo o versión optimista cuando haya base de datos |
| IA-08 | repositorio.py:17 | `guardar_cambio_prioridad` lanza `KeyError` si el ticket no existe | Posible error | Baja | Validar existencia |
| IA-09 | prioridad.py:52 | `ahora` es un parámetro público: si la API lo pasara desde la petición, el cliente podría falsificar la fecha de la auditoría; además acepta fechas sin zona horaria | A09 Integridad de auditoría | Baja | Hacerlo solo por nombre (keyword-only) y exigir zona horaria |

La IA no reportó problemas de inyección SQL, secretos ni contraseñas: no hay base de datos, configuración ni
autenticación en estos archivos.

## Verificación (hecha por mí, no por la IA)

Reproduje cada hallazgo con un script contra el commit `0a04fa6`. Salida:

```text
IA-01 justificación no texto: EXCEPCIÓN NO CONTROLADA AttributeError: 'int' object has no attribute 'strip'
IA-02 justificación de 1 MB: sin error -> 1000000
IA-03 saltos de línea: sin error -> 'ok\n2026-01-01 ADMIN borró auditoría'
IA-04 mutar objeto devuelto: Baja | auditoría: []
IA-05 usuario None: EXCEPCIÓN NO CONTROLADA AttributeError: 'NoneType' object has no attribute 'rol'
IA-06 entrada reflejada: error de dominio PrioridadInvalidaError (400)
IA-08 guardar sin ticket: EXCEPCIÓN NO CONTROLADA KeyError: 9
IA-09 fecha falsificada: sin error -> datetime.datetime(1999, 1, 1, 0, 0)
IA-10 estado 'Cerrado': sin error -> 'Alta'
IA-10b estado ' cerrado': sin error -> 'Alta'
Checklist rol líder: error de dominio PermisoDenegadoError (403)
```

La clasificación final (real o falso positivo) y el motivo están en `revision_seguridad.md`, sección 3.

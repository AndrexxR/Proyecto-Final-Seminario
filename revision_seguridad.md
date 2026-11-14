# Informe de revisión de código y seguridad

Proyecto: Incidencias IA. Clasificación y priorización de incidencias con IA (HU-03)
Estudiante: Carlos Andrés Rueda
Fecha: 2026-11-14
Commit revisado: `0a04fa6` (antes de las correcciones)

## 1. Herramientas y criterios

- **Linter:** ruff 0.16.9 con las reglas E, F, B y S. Configuración en `pyproject.toml` (`line-length = 100`, S101 permitido solo en `tests/`). Antes: 10 avisos E501. Ahora: `All checks passed!`.
- **Auditoría de dependencias:** pip-audit 2.10.1 sobre `requirements-dev.txt`. Resultado: sin vulnerabilidades (`No known vulnerabilities found`).
- **Lista de revisión:** la de la semana 6 (corrección y pruebas, diseño y legibilidad, seguridad).
- **Revisión con IA:** Claude (Claude Code) con el prompt de revisión de la semana (ver sección 3 y `docs/revision_ia.md`).

### Puntos de seguridad revisados

| Punto | ¿Aplica? | Resultado |
|---|---|---|
| Inyección (consultas con parámetros) | No por ahora: no hay base de datos ni SQL; el repositorio es un diccionario en memoria. Se revisaron otras entradas: la justificación permitía inyectar líneas en la auditoría | H-05. Cuando llegue la BD, solo consultas con parámetros (pendiente P-02) |
| Secretos (código, historial, .gitignore, .env.example) | Sí | `git log --all -p` no muestra claves ni contraseñas. `.env` ya estaba en `.gitignore` (comprobado con `git check-ignore`). Faltaba `.env.example`: H-07 |
| Contraseñas (scrypt, bcrypt o argon2 con sal) | No: el sistema no guarda contraseñas; `Usuario` llega ya autenticado y solo tiene id y rol | Sin hallazgos. Cuando haya login: argon2 o bcrypt (P-03) |
| Control de acceso (rol verificado y prueba de abuso) | Sí: solo el rol `soporte` cambia la prioridad | El rol se verifica primero (403 antes que 404). La prueba de abuso solo cubría `operativo`: H-08. El repositorio permitía cambiar la prioridad sin auditoría: H-02 |
| Dependencias (existen, necesarias, versión fijada, pip-audit) | Sí, solo de desarrollo: el código usa la biblioteca estándar | ruff, pytest y pip-audit existen en PyPI, cada una tiene un uso y están fijadas con `==` en `requirements-dev.txt`. pip-audit: sin vulnerabilidades |

## 2. Tabla de hallazgos

Las líneas corresponden al commit revisado `0a04fa6`. Cada corrección tiene su prueba en `tests/test_seguridad.py`.

| Id | Archivo y línea | Problema | Categoría (OWASP o tipo) | Severidad | Corrección | Commit |
|---|---|---|---|---|---|---|
| H-01 | modelos.py:9, prioridad.py:39 | `estado` era texto libre: con `"Cerrado"` o `" cerrado"` un ticket cerrado aceptaba cambios | A04 Diseño inseguro / valor mágico | Media | Constantes `ESTADOS`; `Ticket.__post_init__` rechaza estados y prioridades fuera de la lista | `fe40129` |
| H-02 | repositorio.py:10-11 | `obtener_ticket` devolvía el objeto interno: se podía cambiar la prioridad sin pasar por las reglas ni dejar auditoría | A01 Control de acceso roto (integridad) | Media | El repositorio guarda y devuelve copias (`dataclasses.replace`); prueba de abuso | `3d1d89c` |
| H-03 | prioridad.py:58 | Una justificación que no es texto (`12345`) lanzaba `AttributeError` (error 500) | A04 / validación de entrada | Media | `_normalizar_justificacion` y `JustificacionInvalidaError` (400) | `f72d01d` |
| H-04 | prioridad.py:58 | La justificación no tenía tope: se guardaba 1 MB en la auditoría | A04 / consumo de recursos | Media | `LONGITUD_MAXIMA_JUSTIFICACION = 500`, error 400; pruebas en el límite | `36254c4` |
| H-05 | prioridad.py:58 | Saltos de línea y caracteres de control permitían falsificar líneas en la auditoría o en logs | A09 Fallas de registro (inyección en logs) | Baja | Se rechazan caracteres no imprimibles (400) | `189e2f6` |
| H-06 | prioridad.py:52, 71 | La fecha de la auditoría `ahora` se podía pasar por posición y sin zona horaria | A09 Integridad de la auditoría | Baja | `ahora` es solo por nombre (`*`) y exige zona horaria | `a771a09` |
| H-07 | raíz del repositorio | Faltaba `.env.example` | A05 Configuración (secretos) | Baja | `.env.example` con valores de ejemplo, sin valores reales | `862e4d8` |
| H-08 | tests/test_prioridad.py:117-121 | La prueba de abuso solo cubría el rol `operativo` (no `líder`, `"Soporte"`, `" soporte"`, vacío ni `None`) | A01 Control de acceso (prueba faltante) | Baja | Pruebas de abuso para todos esos roles y de 403 antes que 404 | `ee649a5` |
| H-09 | prioridad.py, modelos.py | Refactor: valores mágicos de estado, limpieza de la justificación mezclada con la regla de negocio, funciones sin docstring | Mantenibilidad | Baja | Constantes, función `_normalizar_justificacion`, docstrings completos y demo `python -m incidencias` | `ccc605c`, `9647b3e` |

**Severidad:** alta (permite acceder o cambiar datos sin permiso, o expone secretos), media (error probable o riesgo con condiciones), baja (estilo o mantenibilidad).

Resultado: 28 pruebas pasan (14 de la semana 5, sin cambios de lógica, y 14 nuevas). La única edición a `tests/test_prioridad.py` es partir una línea larga del helper `crear_repo` (aviso E501, solo formato).

### Avisos del linter no corregidos

| Regla | Archivo y línea | Por qué se mantiene |
|---|---|---|
| E501 (límite subido de 88 a 100) | `pyproject.toml` | Los identificadores en español (`JustificacionRequeridaError`, `prioridad_sugerida`) son largos; con 88 había que partir líneas legibles. Con 100 no queda ningún aviso |
| S101 (ignorada en `tests/**`) | `pyproject.toml` | `assert` es la forma normal de comprobar en pytest. Hoy las pruebas usan `unittest` y el aviso no aparece; se deja para pruebas futuras |

## 3. Revisión con IA

**Prompt usado:** revisor senior con foco en seguridad sobre `modelos.py`, `prioridad.py` y `repositorio.py`, con los criterios de la semana, una tabla con línea, categoría y severidad, y la indicación de separar problemas seguros de sospechas. El texto completo, la respuesta y la salida del script de verificación están en [`docs/revision_ia.md`](docs/revision_ia.md). Bitácora: entradas 7 y 8.

| Hallazgo de la IA | ¿Real o falso positivo? | Cómo lo verifiqué |
|---|---|---|
| IA-01 Justificación que no es texto da 500 | Real (H-03) | `cambiar_prioridad(..., 12345)` lanzó `AttributeError` |
| IA-02 Justificación sin longitud máxima | Real (H-04) | Se guardó una justificación de 1 000 000 de caracteres |
| IA-03 Saltos de línea en la justificación | Real (H-05) | Se guardó `'ok\n2026-01-01 ADMIN borró auditoría'` |
| IA-04 El repositorio devuelve el objeto interno | Real (H-02) | Cambié `prioridad_actual` del objeto devuelto: el repositorio quedó en `Baja` y la auditoría vacía |
| IA-05 `usuario=None` lanza `AttributeError` | Falso positivo | Sí ocurre, pero ningún camino del código pasa `None`: el contrato y el tipo exigen un `Usuario` ya autenticado, y no es un dato que envíe el cliente. Que la futura API rechace con 401 las peticiones sin sesión queda como P-04 |
| IA-06 La entrada aparece en el mensaje (XSS) | Falso positivo | El valor se muestra con `repr` y la API responde JSON; además solo se refleja la prioridad pedida, no datos de otros. Se devuelve 400 correctamente |
| IA-07 Condición de carrera entre leer y guardar | Real, pero no aplica todavía (pendiente P-01) | En memoria y con un solo hilo no se puede reproducir; aparecerá con la base de datos |
| IA-08 `guardar_cambio_prioridad` lanza `KeyError` | Falso positivo | Ocurre si se llama directamente, pero `cambiar_prioridad` valida que el ticket exista antes de guardar; no hay otro camino. Quedó documentado en el docstring |
| IA-09 La fecha de la auditoría se puede falsificar | Real (H-06), severidad baja | Se aceptó `datetime(1999, 1, 1)` sin zona como fecha del cambio |
| IA-10 Estado `"Cerrado"` no se reconoce como cerrado | Real (H-01) | `estado="Cerrado"` y `" cerrado"` permitieron cambiar a `Alta` |

**Lo que la IA no encontró:** (1) faltaba `.env.example` (H-07), y (2) la prueba de abuso de control de acceso solo cubría el rol `operativo` (H-08). Los dos salieron de la lista de revisión de la semana y no del código: la IA solo recibió los archivos fuente, así que no podía ver qué archivos faltaban en el repositorio ni qué casos cubrían las pruebas. Tampoco señaló el límite de línea del linter ni la falta de versiones fijadas (no había archivo de dependencias).

## 4. Pendientes

| Pendiente | Por qué no se corrigió todavía | Plan |
|---|---|---|
| P-01 Condición de carrera (IA-07): dos técnicos cambian la prioridad a la vez | El repositorio es en memoria y de un solo hilo; no se puede reproducir ni corregir de forma realista | Con la base de datos: transacción con `SELECT ... FOR UPDATE` o columna `version` (bloqueo optimista) y prueba concurrente |
| P-02 Inyección SQL | Aún no hay base de datos | Repositorio SQL solo con consultas con parámetros y una prueba que envíe `' OR 1=1 --` |
| P-03 Contraseñas y autenticación | El login no es parte de este incremento | Usar argon2 o bcrypt con sal, nunca MD5 ni SHA-1 |
| P-04 Capa API: autenticación (401) y no tomar `ahora` de la petición | Aún no hay endpoint `PATCH /api/tickets/{id}/prioridad` | Al crear el endpoint: exigir sesión antes de construir el `Usuario` y prueba de que el cliente no puede fijar la fecha |
| P-05 Confirmar con el docente los estados, los niveles de prioridad y el límite de 500 caracteres | El diseño S4 no los define | Preguntar en la sesión de la semana 7 y ajustar las constantes de `modelos.py` |

**Claves expuestas:** Ninguna. Se revisó el historial completo con `git log --all -p` buscando `password`, `secret`, `api_key` y `token`: no hay claves en ningún commit.

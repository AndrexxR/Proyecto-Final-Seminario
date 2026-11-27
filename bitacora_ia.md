# Bitácora de uso de IA

Proyecto: Sistema web de inventarios con clasificación y priorización de incidencias mediante IA
Estudiante: Carlos Andrés Rueda
Funcionalidad: HU-03 Ajuste manual de prioridad por el técnico, con justificación cuando corresponda
Asistente usado: Claude. Al principio en modo chat; desde la revisión de seguridad, Claude Code como agente de código en la rama `claude/wonderful-cerf-d5iioc`

## Entradas

> **Aclaración sobre las entradas 7 a 15.** Esas entradas están escritas en primera persona, pero el trabajo que describen (revisión, correcciones, scripts de reproducción, pruebas, errores introducidos a propósito, datos sintéticos) lo ejecutó el agente Claude Code en la rama `claude/wonderful-cerf-d5iioc`, y cada paso quedó en un commit con `Co-Authored-By: Claude`. Mi papel fue pedir cada tarea y decidir su integración a `main`. Lo explico en el informe final, sección 7.

### Entrada 1

- **Fecha:** 2026-11-13
- **Prompt o sugerencia:** Entregué al asistente el documento de diseño S4 y la guía de la tarea, y le pedí construir la primera funcionalidad con pruebas y la bitácora. El asistente propuso HU-03 y la función `cambiar_prioridad`.
- **Decisión:** Aceptada
- **Por qué:** Es pequeña (una función con casos límite), usa las entidades `Ticket` e `HistorialPrioridad` del diseño y su endpoint ya define errores 400, 404 y 409 en la sección 6 del diseño.
- **Verificación:** Contrasté la función con las secciones 5 (modelo de datos) y 6 (API) del diseño S4. Pendiente de mi parte: comprobar que HU-03 es de prioridad Must en mi documento de requisitos.
- **Commit relacionado:** «Pruebas de cambio manual de prioridad HU-03 (en rojo)»

### Entrada 2

- **Fecha:** 2026-11-13
- **Prompt o sugerencia:** El asistente evaluó hacer la funcionalidad en PHP con PHPUnit y la rechazó para esta entrega, en favor de Python con `unittest`.
- **Decisión:** Rechazada
- **Por qué:** El entorno del asistente no tenía PHP instalado ni acceso a internet para instalarlo, así que no habría podido ejecutar las pruebas en rojo y en verde, que la guía exige mostrar en el historial. El diseño S4 no fija lenguaje y la guía acepta Python.
- **Verificación:** `which php` no devolvió nada; `python3 -m unittest` sí se ejecutó. La lógica (validaciones y auditoría) no depende del lenguaje y puede portarse a PHP.
- **Commit relacionado:** «Pruebas de cambio manual de prioridad HU-03 (en rojo)»

### Entrada 3

- **Fecha:** 2026-11-13
- **Prompt o sugerencia:** Cómo interpretar «justificación cuando corresponda» de HU-03. Primera opción considerada: exigir justificación en todo cambio de prioridad.
- **Decisión:** Aceptada con cambios
- **Por qué:** Exigirla siempre obligaría a justificar incluso cuando el técnico solo vuelve a la sugerencia de la IA. El diseño guarda `prioridad_sugerida` y `prioridad_final` en `HistorialPrioridad`, así que la justificación solo se pide si el técnico se aparta de la sugerencia, o si no hay sugerencia por fallo o timeout de la IA.
- **Verificación:** Dos pruebas lo fijan: `test_volver_a_la_sugerencia_de_la_ia_no_exige_justificacion` y `test_ticket_pendiente_de_clasificacion_exige_justificacion`. También lo dejé escrito como supuesto en el README para confirmarlo con el docente.
- **Commit relacionado:** «Pruebas de cambio manual de prioridad HU-03 (en rojo)»

### Entrada 4

- **Fecha:** 2026-11-13
- **Prompt o sugerencia:** Escribir 14 pruebas a partir del contrato, antes de la implementación: 4 normales, 6 de límite y 4 de error, con nombres que dicen qué prueban. Usé `unittest.TestCase` porque `pytest` no estaba instalado en el entorno del asistente.
- **Decisión:** Aceptada
- **Por qué:** Cubren lo que pide la guía y el criterio de aceptación: cambio correcto, conservación de la sugerencia original, auditoría completa, justificación vacía, ticket pendiente, primer y último valor de la lista, y los errores 400, 403, 404 y 409.
- **Verificación:** Con la función aún sin implementar, `python -m unittest` dio `FAILED (errors=18)`, es decir, las 14 pruebas fallaban (18 con las subpruebas). Falta ejecutar `pytest` en mi equipo para confirmar que también las corre.
- **Commit relacionado:** «Pruebas de cambio manual de prioridad HU-03 (en rojo)»

### Entrada 5

- **Fecha:** 2026-11-13
- **Prompt o sugerencia:** Con el contrato y las pruebas como contexto, implementar `cambiar_prioridad`: validar rol, prioridad, existencia del ticket, estado cerrado y prioridad repetida, exigir justificación según la regla, y guardar el cambio y el registro de auditoría a la vez.
- **Decisión:** Aceptada
- **Por qué:** Cumple el contrato, usa solo la biblioteca estándar y no deja cambios parciales cuando hay un error, porque todas las validaciones ocurren antes de guardar.
- **Verificación:** `python -m unittest` dio `Ran 14 tests ... OK`. Leí el código línea por línea. Además probé 4 mutaciones manuales (invertir la regla de justificación, quitar `strip()`, ignorar el ticket cerrado, auditar mal la sugerida) y cada una hizo fallar al menos una prueba; las revertí sin commitearlas.
- **Commit relacionado:** «Implementa cambiar_prioridad de HU-03 (pruebas en verde: 14 OK)»

### Entrada 6

- **Fecha:** 2026-11-13
- **Prompt o sugerencia:** Refactorizar con las pruebas en verde: partir `cambiar_prioridad` en `_validar_peticion`, `_validar_ticket` y `_exige_justificacion`, para que la regla de HU-03 tenga nombre y la función principal se lea de arriba abajo.
- **Decisión:** Aceptada
- **Por qué:** La función hacía validaciones, regla de negocio y construcción del registro en un solo bloque. Separar la regla en `_exige_justificacion` la hace fácil de explicar y de cambiar si el cliente define otra.
- **Verificación:** `git diff 1bacf77 HEAD -- tests` no muestra cambios (no toqué las pruebas) y `python -m unittest` sigue en `OK` con las 14 pruebas. El orden de las validaciones se mantuvo igual.
- **Commit relacionado:** «Refactor HU-03: extrae _validar_peticion, _validar_ticket y _exige_justificacion; sin cambiar comportamiento ni pruebas»

### Entrada 7

- **Fecha:** 2026-11-14
- **Prompt o sugerencia:** Segunda revisión con IA usando el prompt de revisión del curso (criterios, tabla con línea y severidad, problemas seguros separados de sospechas) sobre `modelos.py`, `prioridad.py` y `repositorio.py`. El prompt y la respuesta completos están en `docs/revision_ia.md`.
- **Decisión:** Aceptada con cambios
- **Por qué:** La IA devolvió 10 hallazgos: 5 «seguros» y 5 «sospechas». No los copié al informe sin más: la clasificación como real o falso positivo depende de lo que pasa en mi código.
- **Verificación:** Escribí un script que reproduce cada hallazgo contra el commit `0a04fa6` (salida en `docs/revision_ia.md`). Resultado: 6 reales (IA-01, 02, 03, 04, 09, 10), 3 falsos positivos (IA-05, 06, 08) y 1 real que pasa a pendientes (IA-07, carrera, porque no hay BD).
- **Commit relacionado:** «Agrega la revisión con IA (prompt, hallazgos y verificación) en docs/revision_ia.md» (`c1c772b`)

### Entrada 8

- **Fecha:** 2026-11-14
- **Prompt o sugerencia:** Tres hallazgos de la IA que rechacé como falsos positivos: IA-05 (`usuario=None`), IA-06 (XSS por mostrar la prioridad en el mensaje de error) e IA-08 (`KeyError` en `guardar_cambio_prioridad`).
- **Decisión:** Rechazada
- **Por qué:** IA-05: ningún camino pasa `None` y el contrato exige un `Usuario` autenticado; lo dejé como requisito de la futura API (P-04). IA-06: el valor se muestra con `repr`, la API responde JSON y solo refleja lo que el mismo cliente envió. IA-08: `cambiar_prioridad` valida la existencia antes de guardar; no hay otro camino.
- **Verificación:** Ejecuté los tres casos: IA-06 sí devuelve un error de dominio 400 controlado. IA-05 e IA-08 lanzan excepción solo si se llama la función de forma distinta a la del contrato. Lo dejé documentado en el docstring de `guardar_cambio_prioridad`.
- **Commit relacionado:** «Agrega revision_seguridad.md…» (sección 3)

### Entrada 9

- **Fecha:** 2026-11-14
- **Prompt o sugerencia:** Corrección de H-01 (IA-10): la IA propuso una lista de estados válidos y validarla al crear el `Ticket`. Consideré también normalizar el estado con `.strip().lower()`.
- **Decisión:** Aceptada con cambios
- **Por qué:** Normalizar escondería datos corruptos en la BD; prefiero rechazarlos con `ValueError`. Además aproveché para quitar los valores mágicos (`ESTADO_ABIERTO`, `ESTADO_PENDIENTE_CLASIFICACION`, `ESTADOS`) y validar también las prioridades guardadas.
- **Verificación:** Prueba nueva con `"Cerrado"`, `" cerrado"`, `"CERRADO"`, `""` y `"borrado"`. Las 14 pruebas originales de HU-03 siguen pasando sin cambios en su lógica: `git diff 0a04fa6 -- tests/test_prioridad.py` solo muestra una línea partida por el linter.
- **Commit relacionado:** «Corrige H-01: Ticket valida estado y prioridades contra listas cerradas» (`fe40129`)

### Entrada 10

- **Fecha:** 2026-11-14
- **Prompt o sugerencia:** Usé Claude Code como agente con una instrucción delimitada: «trabaja en la rama `claude/wonderful-cerf-d5iioc`; configura ruff con E, F, B y S; corrige los hallazgos reales uno por commit, cada uno con una prueba nueva; no modifiques las pruebas existentes para que pasen; escribe docstrings, README e informe».
- **Decisión:** Aceptada
- **Por qué:** Son tareas de varios pasos, pero cada una es pequeña y verificable con pruebas y con el linter. La rama propia me deja revisar el diff antes de integrar.
- **Verificación:** El agente ejecutó `ruff check .` y `python -m pytest` después de cada commit (28 pruebas OK al final) y probó los comandos del README en una carpeta limpia con un venv nuevo. Yo reviso el diff completo de la rama con `git diff 0a04fa6..claude/wonderful-cerf-d5iioc` y cada commit con `git show <hash>` antes de integrarla a `main`.
- **Commit relacionado:** de `c8dfb2f` a `d0c7a19` en la rama `claude/wonderful-cerf-d5iioc`

### Entrada 11

- **Fecha:** 2026-11-14
- **Prompt o sugerencia:** El linter dio 10 avisos E501 (líneas de más de 88 caracteres). Opción 1: partir todas las líneas, incluidas las de las pruebas. Opción 2: subir el límite a 100 en `pyproject.toml`.
- **Decisión:** Aceptada con cambios
- **Por qué:** Elegí 100 porque los nombres en español son largos y partir líneas legibles no mejora el código. La única línea que pasaba de 100 (helper `crear_repo` de las pruebas) la partí, sin cambiar su lógica. Lo justifiqué en el informe.
- **Verificación:** `ruff check .` dice `All checks passed!` y `pip-audit` no encuentra vulnerabilidades. Las versiones de las herramientas quedaron fijadas en `pyproject.toml`.
- **Commit relacionado:** «Configura ruff (E,F,B,S) en pyproject.toml y fija dependencias de desarrollo» (`c8dfb2f`)

### Entrada 12

- **Fecha:** 2026-11-21
- **Prompt o sugerencia:** Diseño de casos. Le di a la IA la regla de cada función (contrato de HU-03 del README) y le pedí: «Para cada regla, propone casos con particiones de equivalencia (un caso por grupo, incluidos los inválidos), valores límite (el último valor de una partición y el primero de la siguiente) y, para `cambiar_prioridad`, una tabla de decisión con todas las combinaciones, simplificada donde una condición no importe. El esperado debe salir de la regla, no del código. Señala las ambigüedades en lugar de resolverlas por tu cuenta».
- **Decisión:** Aceptada con cambios
- **Por qué:** Revisé la propuesta con las cinco preguntas. Particiones y límites: los límites de la longitud tenían que medirse después de quitar los espacios de los extremos, y eso obligó a agregar el caso de 500 con espacios. Origen del esperado: cada esperado tenía que salir de la regla escrita en la sección 1 del registro. Ambigüedades y reglas inventadas: varias cosas que parecían reglas eran interpretaciones (el orden de los errores, si el tabulador es de control, si un salto final cuenta); las dejé como decisiones A1 a A9 y marqué cuáles debo confirmar con el docente. La tabla de decisión pasó de 128 combinaciones a 9 reglas.
- **Verificación:** Contrasté cada fila de las tablas con el texto de la regla. Las ambigüedades A2, A3, A7, A8 y A9 quedan por confirmar.
- **Commit relacionado:** «Registro de pruebas: reglas y tablas de casos de las cuatro funciones» (`e5f7a64`)

### Entrada 13

- **Fecha:** 2026-11-21
- **Prompt o sugerencia:** Generación de pruebas: «Escribe pruebas con pytest para estas cuatro funciones a partir de la regla y de esta tabla. Usa `@pytest.mark.parametrize` con un comentario por fila que diga qué caso de la tabla es, `pytest.raises` con el tipo de error exacto y esperados fijos. No modifiques el código del proyecto».
- **Decisión:** Aceptada con cambios
- **Por qué:** El borrador (34 casos, todos en verde) tenía pruebas débiles: `pytest.raises(Exception)`, límites calculados con la constante del código, `assert ticket is not None`, la tabla de F3 incompleta y ninguna comprobación de que un error no deje cambios. Lo corregí aplicando las tres preguntas a cada prueba; el detalle está en la sección 2 del registro.
- **Verificación:** Metí 5 errores en una copia del código: el borrador dejó pasar 3 (D1, D2 y D4) y la suite revisada los detectó todos. La fila del espacio no separable falló con el código real: revisé la regla, vi que era un defecto del código y corregí el código, no la prueba. `python -m pytest -v`: todo en verde.
- **Commit relacionado:** borrador `37e64b9`, revisión `bf12242` y corrección del código `46aff6a`

### Entrada 14

- **Fecha:** 2026-11-21
- **Prompt o sugerencia:** Datos sintéticos: «Genera en JSON usuarios, tickets y justificaciones para pruebas de un sistema de incidencias de negocios de barrio en Santander, Colombia. Nada de personas reales; teléfonos claramente ficticios; incluye tildes, ñ, apóstrofo, texto vacío, valores en cero, un rol casi correcto ("Soporte") y justificaciones que intenten meter saltos de línea en la auditoría».
- **Decisión:** Aceptada con cambios
- **Por qué:** Los datos traían los casos pedidos. Yo escribí el campo `guardada` (el esperado) de cada justificación a partir de la regla y quité una afirmación del archivo que no podía comprobar (que el bloque `000` nunca se asigna a líneas reales); la cambié por «inventados». No incluí ids en cero porque la regla no los define (A8).
- **Verificación:** Revisé que ningún nombre fuera de alguien conocido ni mío ni de mi familia. La prueba `test_los_datos_traen_los_casos_dificiles` avisa si alguien recorta los casos difíciles. Los datos sirvieron: con el error M5 (rol sin distinguir mayúsculas), la única prueba nueva que falló fue la del usuario sintético con rol `"Soporte"`.
- **Commit relacionado:** «Agrega datos sintéticos con fixture y pruebas que los usan» (`41f3b16`)

### Entrada 15

- **Fecha:** 2026-11-21
- **Prompt o sugerencia:** Romper el código a propósito: cinco errores, uno a la vez (`>` por `>=`, máximo de 500 a 50, `_exige_justificacion` siempre `False`, prioridad repetida solo en tickets abiertos y rol sin distinguir mayúsculas).
- **Decisión:** Aceptada
- **Por qué:** Es la forma de saber si las pruebas protegen las reglas o solo pasan.
- **Verificación:** M4 no hizo fallar ninguna prueba (94 en verde con el código roto). Agregué la fila R5 con un ticket pendiente que ya tiene esa prioridad, y con el mismo error esa fila falla. Deshice cada cambio con `git restore` y comprobé que `git status` quedara limpio.
- **Commit relacionado:** «Agrega el caso de prioridad repetida en ticket pendiente y anota los errores introducidos» (`bc4352b`)

### Entrada 16

- **Fecha:** 2026-11-27
- **Prompt o sugerencia:** Le pedí al agente un pipeline de integración continua con ruff, pytest y pip-audit para el repositorio.
- **Decisión:** Aceptada con cambios
- **Por qué:** La primera versión (`56cd73a`) corría `pip-audit` sin argumentos en Python 3.10 y 3.13. En 3.10 falló por vulnerabilidades en `setuptools` y `filelock`, que no son dependencias del proyecto sino del servidor y del propio pip-audit.
- **Verificación:** La detectó la primera ejecución del pipeline (pruebas y ruff en verde, auditoría en rojo solo en 3.10; el log mostraba los paquetes). El agente separó la auditoría en un trabajo con Python 3.13 y pip y setuptools actualizados (`4572201`).
- **Commit relacionado:** `56cd73a`, `4572201`

### Entrada 17

- **Fecha:** 2026-11-27
- **Prompt o sugerencia:** Le pedí al agente redactar el informe final con la plantilla y las diapositivas de la sustentación, usando solo lo que hay en el repositorio.
- **Decisión:** Aceptada con cambios
- **Por qué:** La fase de fundamentos y los documentos de propuesta, entrevista, diseño S4, despliegue y operación no están en el repositorio, así que el informe lo dice en lugar de inventarlos. Los casos de verificación de la sección 4 salen de commits reales.
- **Verificación:** Cada enlace a un commit o archivo del informe apunta a algo que existe en `main`. Antes de sustentar tengo que releer el informe y ensayar las preguntas.
- **Commit relacionado:** el commit que agrega `informe_final.md` y `docs/sustentacion.pdf`

## Resumen

| Decisión | Cantidad |
|---|---|
| Aceptadas | 6 |
| Aceptadas con cambios | 9 |
| Rechazadas | 2 |

## Errores que atraparon las pruebas

En la fase roja las 14 pruebas fallaron con `NotImplementedError`, lo que confirmó que sí ejercitan la función. La primera implementación pasó todas las pruebas, así que en esta funcionalidad no hubo un defecto de código que una prueba detectara. Lo que sí comprobé es que las pruebas detectan errores: las 4 mutaciones manuales de la entrada 5 hicieron fallar entre 1 y 3 pruebas cada una.

En la revisión de seguridad comprobé que las pruebas nuevas sí detectan los defectos: ejecuté `tests/test_seguridad.py` contra el código del commit `0a04fa6` (agregando solo los nombres nuevos que importa) y dio `18 failed, 8 passed`. Fallan todas las pruebas de H-01 a H-06. Pasan las pruebas de abuso de H-08 (el control de acceso ya funcionaba; faltaba probarlo) y las de casos válidos (texto en el límite, tildes, hora UTC por defecto).

En la suite de reglas, una prueba escrita desde la regla encontró un defecto real: el código rechazaba el espacio no separable, que la regla sí admite (fila F1-P7, corregido en `46aff6a`). Además, de los cinco errores metidos a propósito, uno (M4) no lo detectaba ninguna prueba hasta que agregué el caso que faltaba.

## Reflexión final (5 a 8 líneas)

El asistente me ayudó más a traducir el diseño S4 en un contrato concreto: encontró las reglas implícitas (qué pasa con un ticket sin sugerencia de IA, qué es «cuando corresponda») y me obligó a escribirlas como supuestos y pruebas. Las pruebas en rojo primero me sirvieron para fijar la regla de la justificación antes de ver el código. En esta ocasión no atraparon un error de implementación; sí atraparon las 4 mutaciones que probé, y eso me da confianza en que protegen la regla. No pude usar PHP en este entorno, así que lo haría diferente en la próxima funcionalidad: ejecutar las pruebas en el mismo lenguaje del sistema real desde el primer commit. También confirmaría con el docente los niveles de prioridad y los estados, que el diseño no define.

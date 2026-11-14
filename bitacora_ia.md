# Bitácora de uso de IA

Proyecto: Sistema web de inventarios con clasificación y priorización de incidencias mediante IA
Estudiante: Carlos Andrés Rueda
Funcionalidad: HU-03 Ajuste manual de prioridad por el técnico, con justificación cuando corresponda
Asistente usado: Claude, en modo chat (no agente ni autocompletado en el IDE)

## Entradas

### Entrada 1

- **Fecha:** 2026-11-13
- **Prompt o sugerencia:** Entregué al asistente el documento de diseño S4 y la guía de la tarea de la semana 5, y le pedí construir la primera funcionalidad con pruebas y la bitácora. El asistente propuso HU-03 y la función `cambiar_prioridad`.
- **Decisión:** Aceptada
- **Por qué:** Es pequeña (una función con casos límite), usa las entidades `Ticket` e `HistorialPrioridad` del diseño y su endpoint ya define errores 400, 404 y 409 en la sección 6 del diseño.
- **Verificación:** Contrasté la función con las secciones 5 (modelo de datos) y 6 (API) del diseño S4. Pendiente de mi parte: comprobar que HU-03 es de prioridad Must en mi documento de la semana 3.
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

## Resumen

| Decisión | Cantidad |
|---|---|
| Aceptadas | 4 |
| Aceptadas con cambios | 1 |
| Rechazadas | 1 |

## Errores que atraparon las pruebas

En la fase roja las 14 pruebas fallaron con `NotImplementedError`, lo que confirmó que sí ejercitan la función. La primera implementación pasó todas las pruebas, así que en esta funcionalidad no hubo un defecto de código que una prueba detectara. Lo que sí comprobé es que las pruebas detectan errores: las 4 mutaciones manuales de la entrada 5 hicieron fallar entre 1 y 3 pruebas cada una.

## Reflexión final (5 a 8 líneas)

El asistente me ayudó más a traducir el diseño S4 en un contrato concreto: encontró las reglas implícitas (qué pasa con un ticket sin sugerencia de IA, qué es «cuando corresponda») y me obligó a escribirlas como supuestos y pruebas. Las pruebas en rojo primero me sirvieron para fijar la regla de la justificación antes de ver el código. En esta ocasión no atraparon un error de implementación; sí atraparon las 4 mutaciones que probé, y eso me da confianza en que protegen la regla. No pude usar PHP en este entorno, así que lo haría diferente en la próxima funcionalidad: ejecutar las pruebas en el mismo lenguaje del sistema real desde el primer commit. También confirmaría con el docente los niveles de prioridad y los estados, que el diseño no define.

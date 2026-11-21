# Registro de pruebas

Proyecto: Incidencias IA. Ajuste manual de prioridad (HU-03)
Estudiante: Carlos Andrés Rueda
Fecha: 2026-11-21

Pruebas de esta semana: `tests/test_reglas.py` (pytest, con `parametrize`) y los datos sintéticos en `tests/datos/` con su fixture en `tests/conftest.py`. Las pruebas de semanas anteriores (`test_prioridad.py`, `test_seguridad.py`) siguen en la suite sin cambios.

Ejecución: `python -m pytest -v`

## 1. Reglas y tablas de casos

El esperado de cada caso sale de la regla escrita aquí, que es la del contrato de HU-03 del README (historia de usuario y criterio de aceptación). No sale de ejecutar el código.

No hay cálculos con decimales en el proyecto, así que `pytest.approx` no aplica.

### F1. `_normalizar_justificacion(justificacion)`: validación de la justificación

**Regla.** La justificación es texto. Una justificación ausente, vacía o de solo espacios cuenta como ausente (`None`). Se guarda sin espacios al inicio ni al final. Admite hasta 500 caracteres, sin saltos de línea ni caracteres de control. Si no es texto, si pasa de 500 o si tiene saltos de línea o caracteres de control, se rechaza con `JustificacionInvalidaError` (400).

**Particiones de equivalencia**

| Id | Partición | Entrada | Esperado |
|---|---|---|---|
| F1-P1 | Ausente | `None` | `None` |
| F1-P2 | Vacía | `""` | `None` |
| F1-P3 | Solo espacios | `"   "` | `None` |
| F1-P4 | Texto válido | `"Afecta el cierre de caja"` | el mismo texto |
| F1-P5 | Texto válido con espacios en los extremos | `"  Afecta caja  "` | `"Afecta caja"` |
| F1-P6 | Texto con tildes, ñ, apóstrofo y signos | `"Señal débil en la sede de D'Artagnan, ¿urgente?"` | el mismo texto |
| F1-P7 | Espacio no separable dentro del texto (no es salto ni control) | `"Caja 2 bloqueada"` | el mismo texto |
| F1-P8 | No es texto (inválida) | `12345`, `["x"]`, `{"m": "x"}` | `JustificacionInvalidaError` |
| F1-P9 | Salto de línea dentro del texto (inválida) | `"línea 1\nlínea 2"`, `"a\rb"` | `JustificacionInvalidaError` |
| F1-P10 | Caracter de control dentro del texto (inválida) | `"a\x00b"`, `"a\x1b[2Jb"`, `"a\tb"` | `JustificacionInvalidaError` |
| F1-P11 | Más larga que el máximo (inválida) | 600 caracteres | `JustificacionInvalidaError` |

**Valores límite** (longitud medida después de quitar los espacios de los extremos)

| Id | Borde | Entrada | Esperado |
|---|---|---|---|
| F1-L1 | Último de «ausente» | 0 caracteres útiles (`""`) | `None` |
| F1-L2 | Primero de «válida» | 1 caracter (`"x"`) | `"x"` |
| F1-L3 | Último de «válida» | 500 caracteres | el mismo texto |
| F1-L4 | Primero de «demasiado larga» | 501 caracteres | `JustificacionInvalidaError` |
| F1-L5 | 500 útiles con espacios en los extremos | `"  " + 500 + "  "` | los 500 caracteres |

### F2. `Ticket(...)`: validación del estado y de las prioridades guardadas

**Regla.** El estado de un ticket es exactamente uno de `abierto`, `pendiente_clasificacion` o `cerrado`. La prioridad sugerida y la vigente son `None` (análisis pendiente) o exactamente una de `Baja`, `Media` o `Alta`. Cualquier otro valor se rechaza con `ValueError` al crear el ticket.

**Particiones de equivalencia**

| Id | Campo | Partición | Entrada | Esperado |
|---|---|---|---|---|
| F2-P1 | estado | Válido | `abierto`, `pendiente_clasificacion`, `cerrado` | se crea |
| F2-P2 | estado | Otra capitalización (inválida) | `Cerrado`, `ABIERTO` | `ValueError` |
| F2-P3 | estado | Con espacios (inválida) | `" cerrado"`, `"abierto "` | `ValueError` |
| F2-P4 | estado | Fuera de la lista o vacío (inválida) | `borrado`, `""`, `None` | `ValueError` |
| F2-P5 | prioridades | `None` (sin análisis) | sugerida y vigente `None` | se crea |
| F2-P6 | prioridades | Válida | `Baja`, `Media`, `Alta` | se crea |
| F2-P7 | prioridad sugerida | Inválida | `alta`, `Urgente`, `""` | `ValueError` |
| F2-P8 | prioridad vigente | Inválida | `alta`, `Urgente`, `""` | `ValueError` |

**Valores límite.** Son listas cerradas, sin orden numérico. Los bordes son el primer y el último valor de cada lista (`abierto` y `cerrado`; `Baja` y `Alta`) y los valores más cercanos fuera de ella (una letra cambiada de mayúscula, un espacio de más, texto vacío).

### F3. `_exige_justificacion(ticket, nueva_prioridad)`: cuándo es obligatoria la justificación

**Regla.** La justificación es obligatoria cuando la nueva prioridad es distinta de la sugerida por la IA. Si el ticket no tiene sugerencia (`None`), siempre se exige. Si la nueva prioridad coincide con la sugerida, es opcional.

**Tabla completa** (son pocas combinaciones, así que van todas: 4 sugeridas × 3 nuevas = 12)

| Sugerida \ Nueva | Baja | Media | Alta |
|---|---|---|---|
| `None` | exige | exige | exige |
| Baja | no exige | exige | exige |
| Media | exige | no exige | exige |
| Alta | exige | exige | no exige |

Particiones: sin sugerencia (exige), coincide con la sugerida (no exige), se aparta de la sugerida (exige).

### F4. `cambiar_prioridad(...)`: varias condiciones, con tabla de decisión

**Regla.** Solo el rol `soporte`, escrito exacto, cambia la prioridad. La prioridad debe estar en la lista. El ticket debe existir, no estar cerrado y no tener ya esa prioridad. La justificación se exige según F3 y se valida según F1. Si todo se cumple, la prioridad vigente pasa a ser la nueva, la sugerida no cambia y se guarda un registro de auditoría con usuario, fecha, prioridad anterior, sugerida, final y justificación. Un error no deja cambios ni registro.

**Condiciones**

- C1: el rol es `soporte`
- C2: la prioridad pedida está en la lista
- C3: el ticket existe
- C4: el ticket está cerrado
- C5: la prioridad pedida es igual a la vigente
- C6: la prioridad pedida coincide con la sugerida (con sugerida `None` cuenta como «no»)
- C7: hay justificación (no vacía, ni de solo espacios)

**Tabla de decisión simplificada.** Las 7 condiciones dan 128 combinaciones. «—» significa que la condición no importa porque una anterior ya decide el resultado.

| Regla | C1 | C2 | C3 | C4 | C5 | C6 | C7 | Resultado |
|---|---|---|---|---|---|---|---|---|
| R1 | No | — | — | — | — | — | — | `PermisoDenegadoError` (403) |
| R2 | Sí | No | — | — | — | — | — | `PrioridadInvalidaError` (400) |
| R3 | Sí | Sí | No | — | — | — | — | `TicketNoEncontradoError` (404) |
| R4 | Sí | Sí | Sí | Sí | — | — | — | `ConflictoError` (409) |
| R5 | Sí | Sí | Sí | No | Sí | — | — | `ConflictoError` (409) |
| R6 | Sí | Sí | Sí | No | No | No | No | `JustificacionRequeridaError` (400) |
| R7 | Sí | Sí | Sí | No | No | No | Sí | Cambia; guarda la justificación |
| R8 | Sí | Sí | Sí | No | No | Sí | No | Cambia; justificación `None` |
| R9 | Sí | Sí | Sí | No | No | Sí | Sí | Cambia; guarda la justificación |

En R1 a R6 además se comprueba que la prioridad vigente no cambió y que no hay registro de auditoría. En R7 a R9 se comprueban todos los campos del registro y que la sugerida no cambió.

**Ambigüedades de las reglas y cómo las decidí**

| # | Ambigüedad | Decisión | Estado |
|---|---|---|---|
| A1 | Si fallan varias condiciones a la vez, ¿qué error sale primero? La regla no fija el orden | El de la tabla: primero el permiso (403), para que un usuario sin permiso no averigüe si un ticket existe (decidido en la revisión de seguridad de la semana 6) | Decidido |
| A2 | ¿Los 500 caracteres se cuentan antes o después de quitar los espacios de los extremos? | Después: se cuenta lo que se guarda | Por confirmar con el docente |
| A3 | ¿Un salto de línea al final (lo que agrega un cuadro de texto al pulsar Enter) cuenta como «salto de línea»? | No: se quita junto con los espacios de los extremos y no llega a la auditoría. Solo se rechaza un salto dentro del texto | Por confirmar |
| A4 | ¿El tabulador es un «caracter de control»? | Sí: en Unicode es de control (categoría Cc), así que se rechaza | Decidido |
| A5 | ¿Un espacio no separable (lo pega Word o el navegador) es válido? | Sí: no es salto de línea ni caracter de control | Decidido |
| A6 | Si la justificación es opcional (R8/R9) pero viene inválida (por ejemplo, un número), ¿se ignora o se rechaza? | Se rechaza con 400: lo que se guarda en la auditoría siempre debe ser válido | Decidido |
| A7 | ¿Un ticket `pendiente_clasificacion` pasa a `abierto` después del cambio manual? | La regla no lo dice; hoy el estado no cambia | Por confirmar con el docente |
| A8 | ¿Puede existir un ticket o usuario con id 0? | La regla no lo dice y no lo pruebo; con la base de datos los ids empiezan en 1 | Pendiente para la semana de la BD |
| A9 | ¿Los caracteres «de formato» invisibles (categoría Cf, como U+200B o el que invierte el sentido del texto, U+202E) cuentan como «de control»? | Con la regla literal, no: Unicode no los llama de control. Pero U+202E puede servir para disfrazar el texto de la auditoría | Por confirmar con el docente; no tienen prueba hasta decidirlo |

## 2. Revisión de las pruebas generadas por la IA

La IA generó un primer borrador de `tests/test_reglas.py` a partir de la regla y de las tablas de la sección 1 (commit `37e64b9`, 34 casos, todos en verde). A cada prueba le apliqué las tres preguntas: (1) ¿el esperado sale de la regla?, (2) ¿fallaría si rompo el código?, (3) ¿cubre algo que otra prueba no cubre? La versión revisada es el commit `bf12242`.

Para responder la pregunta 2 con evidencia y no a ojo, metí 5 errores en una copia del código y corrí el borrador contra cada uno:

| Error metido en la copia | Borrador (`37e64b9`) | Suite revisada |
|---|---|---|
| D1. Quitar la validación de tipo (vuelve el `AttributeError` de la semana 6) | 34 passed: **no lo detecta** | 4 failed |
| D2. Cambiar el máximo de 500 a 5000 | 34 passed: **no lo detecta** | 2 failed |
| D3. Guardar el cambio antes de exigir la justificación | 3 failed | 8 failed |
| D4. Guardar en la auditoría la prioridad final como si fuera la sugerida | 34 passed: **no lo detecta** | 2 failed |
| D5. No exigir justificación cuando no hay sugerencia | 1 failed | 4 failed |

**Pruebas corregidas o descartadas**

| Prueba del borrador | Pregunta que no pasó | Decisión | Razón | Qué hice en su lugar |
|---|---|---|---|---|
| `test_normalizar_justificacion_invalidas` | 1 y 2 | Corregida | Usaba `pytest.raises(Exception)`: el esperado no era el error de la regla (400) y aceptaba cualquier fallo, incluso un `AttributeError`. Por eso no detectó D1. Ruff también la marcó (B017) | `pytest.raises(JustificacionInvalidaError)` y se comprueba `codigo_http == 400` |
| Fila `"x" * (LONGITUD_MAXIMA_JUSTIFICACION + 1)` y `test_normalizar_justificacion_en_el_maximo` | 1 y 2 | Corregidas | El esperado salía de la constante del código, no de la regla («hasta 500»). Si alguien cambia la constante, la prueba cambia con ella; por eso no detectó D2 | Esperados fijos: 499, 500 y 501 caracteres, más el caso de 500 con espacios en los extremos (A2) |
| `test_ticket_con_estado_valido_se_crea` | 2 | Corregida | `assert ticket is not None` nunca puede fallar: un constructor no devuelve `None` | Se comparan el estado y las dos prioridades del ticket creado; se agregaron los casos con prioridades `None` |
| `test_exige_justificacion` | 2 | Corregida | Tenía 4 de las 12 combinaciones de la tabla; faltaban las sugeridas `Baja` y `Alta` | Tabla completa de 12 filas y `is esperado` (antes `==`, que acepta 1 y 0 como si fueran booleanos) |
| `test_cambiar_prioridad_errores` | 2 | Corregida | Solo revisaba el tipo de error; la regla también dice que un error no deja cambios ni auditoría | Se comprueban el código HTTP, la prioridad vigente sin cambio y la auditoría vacía |
| Fila R1 del borrador (operativo con todo lo demás válido) | 3 | Corregida | Repetía `test_usuario_que_no_es_tecnico_no_puede_cambiar_la_prioridad` de la semana 5 y no probaba lo que dice la tabla: en R1 lo demás «no importa» | La fila R1 ahora trae un operativo con ticket inexistente y prioridad inválida, y debe dar 403 (A1) |
| `test_cambiar_prioridad_exitoso` | 2 | Corregida | `len(repo.auditoria) == 1` no revisa el contenido del registro; por eso no detectó D4 | Se compara el `RegistroAuditoria` completo y se revisa que la sugerida no cambió |
| Filas de estado `"Cerrado"`, `" cerrado"`, `"borrado"`, `""` | 3 | Conservadas | Repiten valores de `test_seguridad.py`, pero aquí forman parte de la tabla de particiones de F2 con un caso por partición | Se completaron las particiones que faltaban (`"ABIERTO"`, `"abierto "`, `None`) |

**Casos que faltaban en el borrador y agregué**

- F1: tildes, ñ y apóstrofo (P6); espacio no separable (P7); lista y diccionario (P8); `\r`, `\u2028` y `\u2029` (P9); escape de terminal y tabulador (P10); 1 caracter (L2); 500 con espacios (L5); salto de línea al final (A3).
- F4: la segunda fila de R6 (sin sugerencia y con justificación de solo espacios), R7 sin sugerencia, R8 con justificación de solo espacios y la justificación opcional pero inválida (A6).

**Defecto real que encontró una prueba.** La fila F1-P7 (espacio no separable) falló con el código. Revisé la regla antes de tocar la prueba: solo prohíbe saltos de línea y caracteres de control, y el espacio no separable no es ninguna de las dos cosas. El código usaba `isprintable()`, que rechaza más de lo que dice la regla. No cambié el esperado: corregí el código para rechazar solo las categorías Unicode `Cc`, `Zl` y `Zp` (commit `46aff6a`).

**Ninguna prueba se ajustó al código.** La única prueba que falló reveló un defecto del código, y lo que se corrigió fue el código. Las pruebas de las semanas 5 y 6 no se tocaron.

## 3. Errores introducidos a propósito

_(se completa en el paso 5)_

## 4. Datos de prueba sintéticos

_(se completa en el paso 6)_

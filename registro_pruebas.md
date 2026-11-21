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

## 2. Revisión de las pruebas generadas por la IA

_(se completa después de generar las pruebas)_

## 3. Errores introducidos a propósito

_(se completa en el paso 5)_

## 4. Datos de prueba sintéticos

_(se completa en el paso 6)_

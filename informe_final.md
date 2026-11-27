# Informe final del proyecto integrador

Proyecto: Incidencias IA. Clasificación y priorización de incidencias con IA (módulo de ajuste manual de prioridad, HU-03)
Estudiante: Carlos Andrés Rueda
Repositorio: https://github.com/AndrexxR/Proyecto-Final-Seminario
Fecha: 2026-11-27

> **Cómo leer los enlaces.** `[c:abc1234]` es un commit del repositorio, y los nombres de archivo enlazan al archivo en `main`. La bitácora de uso de IA está en [`bitacora_ia.md`](bitacora_ia.md), con las entradas numeradas (E1, E2…).
>
> **Quién hizo qué.** En requisitos y diseño usé ChatGPT como apoyo para redactar, y yo revisé y corregí sus propuestas ([`docs/requisitos.pdf`](docs/requisitos.pdf), sección 7; [`docs/diseno_S4.pdf`](docs/diseno_S4.pdf), sección 7). Para el código usé Claude en dos modos. Al principio fue un asistente en chat: yo pegaba sus respuestas y hacía los commits (bitácora E1 a E6). Después usé Claude Code como **agente de código**, en la rama `claude/wonderful-cerf-d5iioc`, para la revisión de seguridad, la suite de pruebas, el pipeline y la redacción de este informe. En esas fases el agente escribió el código, ejecutó las verificaciones que describo (scripts de reproducción, errores introducidos a propósito, pipeline) y dejó cada paso en un commit con la línea `Co-Authored-By: Claude`. Mi papel fue pedir cada tarea, decidir cuándo integrarla a `main` y responder por el resultado. Lo detallo en la sección 7, porque es también mi principal aprendizaje.

## 1. Resumen

En un almacén o negocio de barrio que maneja su inventario en un sistema web, cada incidencia (el datáfono no conecta, el inventario no cuadra) recibe de la IA una **prioridad sugerida**. El técnico de soporte necesita corregir esa prioridad cuando la IA se equivoca, y la empresa necesita saber **quién cambió qué y por qué**. Construí la funcionalidad HU-03: el técnico cambia la prioridad, debe justificar cuando se aparta de la IA y cada cambio deja un registro de auditoría. Usé IA en las fases de requisitos y diseño (ChatGPT) y en las de código, pruebas y operación (Claude y Claude Code); de la fase de fundamentos no hay evidencia de uso de IA. Las verificaciones encontraron fallas reales en lo que produjo la IA. Por ejemplo, inventó requisitos sin respaldo en la entrevista, un borrador del modelo de datos perdía la prioridad sugerida, su implementación dejaba cambiar tickets cerrados escritos como `"Cerrado"` y su primer borrador de pruebas dejaba pasar 3 de 5 errores. Hoy el proyecto tiene **116 pruebas** en verde, ruff sin avisos y un pipeline de integración continua en verde.

## 2. Problema y usuario

**Usuario.** El técnico de soporte que atiende las incidencias del sistema web de inventarios. Otros actores: el usuario operativo, que registra la incidencia, y el líder de operaciones y soporte, que consulta la auditoría ([`docs/requisitos.pdf`](docs/requisitos.pdf), sección 2).

**Cómo lo resolvía antes.** Leyendo uno por uno reportes sin clasificar. En la entrevista con el cliente (un compañero hizo el papel del líder de operaciones; 20/10/2026, 18 minutos, con autorización para grabar y procesar la transcripción con IA) aparecieron frases como «Perdemos horas leyendo reportes para saber cuál es urgente y cuál puede esperar» (N-01) y «A veces el sistema sugiere algo pero el técnico debe tener la última palabra» (N-03).

**Qué necesita.** Que la IA clasifique, priorice y resuma cada ticket (HU-01, HU-02), ver los tickets ordenados por urgencia (HU-04) y poder **corregir la prioridad que sugiere la IA** con trazabilidad (HU-03, prioridad Must: «garantiza el control humano ante fallos del modelo»). Este proyecto implementa HU-03: el técnico corrige la prioridad dentro del sistema, se conserva lo que sugirió la IA, debe justificar cuando se aparta de ella y cada cambio queda auditado. La historia y su criterio de aceptación están en el [README, sección 1](README.md#1-qué-es).

**Limitación de la evidencia.** La propuesta del módulo 1 y la transcripción de la entrevista no están en el repositorio; el problema sale del documento de requisitos, que cita la entrevista.

## 3. La IA en el ciclo de vida

| Módulo y fase | Qué hice con IA | Herramienta | Evidencia (enlace) | Cómo verifiqué |
|---|---|---|---|---|
| 1. Fundamentos | Sin evidencia de uso de IA: la propuesta del módulo 1 no está en el repositorio. El problema y el alcance quedaron en la introducción del documento de requisitos | — | [`docs/requisitos.pdf`](docs/requisitos.pdf), sección 1 | — |
| 2. Requisitos | La IA estructuró las historias de usuario a partir de la transcripción de la entrevista, generó los escenarios Gherkin y sugirió atributos de calidad ISO/IEC 25010 | ChatGPT | [`docs/requisitos.pdf`](docs/requisitos.pdf), secciones 4 a 7 | Revisión INVEST de cada historia; cada necesidad lleva una cita textual del cliente; se descartaron los requisitos sin cita (caso 1); se cambiaron adjetivos ambiguos por metas numéricas (3,0 s, 99 %, ≤ 25 palabras) |
| 3. Diseño | Matriz de alternativas, diagramas C4, modelo de datos, API y ADR-001 (web cliente-servidor por capas) | ChatGPT | [`docs/diseno_S4.pdf`](docs/diseno_S4.pdf), secciones 2 a 7 | Contraste de cada actor, entidad y endpoint con HU-01 a HU-08; revisión de coherencia entre matriz, diagramas, modelo y API (prompt 4); se corrigió el borrador del modelo de datos (caso 2) |
| 4. Código | Implementación de HU-03 a partir del contrato; luego una revisión de seguridad con IA y 8 correcciones, una por commit | Claude (chat) para la implementación; Claude Code (agente) para la revisión y las correcciones | [c:76e8596](https://github.com/AndrexxR/Proyecto-Final-Seminario/commit/76e8596); [`revision_seguridad.md`](revision_seguridad.md); [`docs/revision_ia.md`](docs/revision_ia.md); bitácora E5 y E7 a E11 | Pruebas, ruff (E, F, B, S) y un script que reproduce cada hallazgo de la IA: 6 reales, 3 falsos positivos ([`docs/revision_ia.md`](docs/revision_ia.md)) |
| 5. Pruebas | Pruebas primero (TDD); luego diseño de casos con particiones, límites y tabla de decisión; pruebas generadas con pytest; datos sintéticos | Claude (chat) y Claude Code (agente) | [`registro_pruebas.md`](registro_pruebas.md); [`tests/test_reglas.py`](tests/test_reglas.py); [`tests/datos/`](tests/datos/datos_sinteticos.json); bitácora E4 y E12 a E15 | Borrador contra versión revisada ([c:37e64b9](https://github.com/AndrexxR/Proyecto-Final-Seminario/commit/37e64b9) frente a [c:bf12242](https://github.com/AndrexxR/Proyecto-Final-Seminario/commit/bf12242)); 5 errores introducidos a propósito (registro, sección 3) |
| 6. Operación | Pipeline de integración continua (ruff, pytest en Python 3.10 y 3.13, pip-audit) y guía de instalación y ejecución | Claude Code (agente) | [`.github/workflows/ci.yml`](.github/workflows/ci.yml); [ejecuciones del pipeline](https://github.com/AndrexxR/Proyecto-Final-Seminario/actions/workflows/ci.yml); [README, secciones 3 a 5](README.md#3-instalación); bitácora E16 | La primera ejecución falló en 3.10 y se corrigió ([c:4572201](https://github.com/AndrexxR/Proyecto-Final-Seminario/commit/4572201)); comandos del README probados en un clon limpio |

## 4. Verificación: lo que la IA hizo mal y cómo lo encontraste

Hay casos de cinco fases: requisitos (1), diseño (2), código (3, 5, 7 y 8), pruebas (4) y operación (6).

### Caso 1: la IA inventó requisitos que el cliente nunca pidió

- **Fase:** requisitos
- **Qué propuso la IA:** al estructurar las historias a partir de la transcripción de la entrevista, ChatGPT agregó «Envío de correos automáticos» y «Asignación automática a técnicos según carga».
- **Qué estaba mal:** ninguna de las dos tiene una cita del cliente que la respalde. Habrían ampliado el alcance (y los datos personales que maneja el sistema) sin una necesidad real.
- **Cómo lo detecté:** cada necesidad del documento debía llevar una cita textual de la entrevista (tabla N-01 a N-06); estas dos no tenían cita.
- **Qué hice:** las descarté y dejé registrado el hallazgo en la sección 7 del [documento de requisitos](docs/requisitos.pdf). Tampoco aparecen en el diseño ([`docs/diseno_S4.pdf`](docs/diseno_S4.pdf), «correcciones adicionales», punto 5). El documento está en el repositorio desde [c:6e32e20](https://github.com/AndrexxR/Proyecto-Final-Seminario/commit/6e32e20).

### Caso 2: el borrador del modelo de datos perdía la prioridad sugerida por la IA

- **Fase:** diseño
- **Qué propuso la IA:** según la revisión registrada en el documento de diseño, el diseño inicial «podía guardar solo la prioridad actual y perder la sugerencia original», y el primer borrador de contenedores podía «mezclar auditoría con datos operativos».
- **Qué estaba mal:** al corregir la prioridad se perdía lo que había sugerido la IA, y con eso la posibilidad de auditar al modelo (HU-07) y de demostrar que la decisión final fue humana (N-03). El borrador además podía registrar datos personales innecesarios.
- **Cómo lo detecté:** contrastando cada entidad con las historias HU-03 y HU-07 ([`docs/diseno_S4.pdf`](docs/diseno_S4.pdf), sección 7, prompts 2 y 3).
- **Qué hice:** separé `prioridad_sugerida` de `prioridad_actual`, agregué la entidad `HistorialPrioridad` y separé la auditoría de la base operativa. Esa decisión llegó al código: `Ticket` tiene los dos campos, `cambiar_prioridad` nunca modifica la sugerida y la prueba `test_corregir_prioridad_conserva_la_sugerencia_original_de_la_ia` lo comprueba ([c:1bacf77](https://github.com/AndrexxR/Proyecto-Final-Seminario/commit/1bacf77)).

### Caso 3: la implementación dejaba cambiar la prioridad de un ticket cerrado

- **Fase:** código
- **Qué propuso la IA:** la implementación de HU-03 ([c:76e8596](https://github.com/AndrexxR/Proyecto-Final-Seminario/commit/76e8596)) bloqueaba los tickets cerrados con `if ticket.estado == ESTADO_CERRADO`, y el estado era texto libre.
- **Qué estaba mal:** un ticket guardado como `"Cerrado"` o `" cerrado"` no se reconocía como cerrado y aceptaba el cambio. Las 14 pruebas originales pasaban, porque todas usaban `"cerrado"` bien escrito.
- **Cómo se detectó:** en la revisión de seguridad con la lista del curso. La IA lo reportó como hallazgo IA-10 y un script lo reprodujo antes de aceptarlo: `IA-10 estado 'Cerrado': sin error -> 'Alta'` ([`docs/revision_ia.md`](docs/revision_ia.md), sección «Verificación»).
- **Qué se hizo:** `Ticket` valida el estado contra una lista cerrada (`ESTADOS`) y lanza `ValueError`, con una prueba nueva ([c:fe40129](https://github.com/AndrexxR/Proyecto-Final-Seminario/commit/fe40129)). Contra el código anterior, esa prueba falla ([`bitacora_ia.md`](bitacora_ia.md), «Errores que atraparon las pruebas»).
- **Lo que enseña:** la misma IA que escribió el código encontró el defecto solo cuando se le pidió revisar con criterios de seguridad. Las pruebas en verde no lo veían.

### Caso 4: el borrador de pruebas daba 34 en verde, pero dejaba pasar 3 de 5 errores

- **Fase:** pruebas
- **Qué propuso la IA:** un borrador de [`tests/test_reglas.py`](tests/test_reglas.py) generado a partir de la regla y de las tablas, guardado sin cambios en [c:37e64b9](https://github.com/AndrexxR/Proyecto-Final-Seminario/commit/37e64b9). Incluía `pytest.raises(Exception)`, límites calculados con `LONGITUD_MAXIMA_JUSTIFICACION + 1` y `assert ticket is not None`.
- **Qué estaba mal:** las pruebas eran débiles. `Exception` acepta cualquier error, incluso el `AttributeError` corregido en la revisión de seguridad. Un esperado sacado de la constante del código cambia junto con el código. Y una aserción que nunca puede fallar no prueba nada.
- **Cómo se detectó:** ruff marcó `B017` (assert de una excepción genérica). Después se introdujeron 5 errores en una copia del código y se corrió el borrador contra cada uno. Con D1 (quitar la validación de tipo), D2 (máximo de 500 a 5000) y D4 (auditar mal la sugerida), el borrador dio «34 passed».
- **Qué se hizo:** tipo de error exacto con su código 400, esperados fijos (499, 500 y 501), tabla de F3 completa (12 combinaciones) y comprobación de que un error no deja cambios ni auditoría ([c:bf12242](https://github.com/AndrexxR/Proyecto-Final-Seminario/commit/bf12242)). La versión revisada detecta los 5 errores. Cada decisión está en [`registro_pruebas.md`, sección 2](registro_pruebas.md#2-revisión-de-las-pruebas-generadas-por-la-ia).

### Caso 5: la validación de la IA rechazaba más de lo que dice la regla

- **Fase:** código, detectado en pruebas
- **Qué propuso la IA:** para corregir el hallazgo H-05 (inyección de líneas en la auditoría), la IA usó `if any(not c.isprintable() for c in limpia)` ([c:189e2f6](https://github.com/AndrexxR/Proyecto-Final-Seminario/commit/189e2f6)).
- **Qué estaba mal:** la regla solo prohíbe saltos de línea y caracteres de control, pero `isprintable()` también rechaza el espacio no separable (U+00A0), que aparece al pegar texto desde Word o el navegador. Un técnico que pegara «Caja 2 bloqueada» desde un correo recibiría un error 400 sin entender por qué.
- **Cómo se detectó:** con una prueba escrita desde la regla, no desde el código. La fila F1-P7 de la tabla de particiones (ambigüedad A5 del registro) falló con el código real. Primero se revisó la regla, no la prueba.
- **Qué se hizo:** se corrigió el código, no el esperado. Ahora se rechazan solo las categorías Unicode `Cc`, `Zl` y `Zp` ([c:46aff6a](https://github.com/AndrexxR/Proyecto-Final-Seminario/commit/46aff6a)), y se agregaron filas para U+2028 y U+2029.

### Caso 6: el primer pipeline falló por auditar el entorno equivocado

- **Fase:** operación
- **Qué propuso la IA:** un pipeline que corría `pip-audit` en todas las versiones de Python ([c:56cd73a](https://github.com/AndrexxR/Proyecto-Final-Seminario/commit/56cd73a)).
- **Qué estaba mal:** `pip-audit` sin argumentos audita **todo** el entorno del servidor. En Python 3.10 reportó vulnerabilidades en `setuptools` (preinstalado en el servidor) y en `filelock` (dependencia del propio pip-audit), y el pipeline quedó en rojo. Ninguna era del proyecto, que no tiene dependencias de ejecución.
- **Cómo se detectó:** por la ejecución misma del pipeline. Las pruebas y ruff pasaron en las dos versiones; el paso «Auditoría de dependencias» falló solo en 3.10, y el log mostraba los paquetes.
- **Qué se hizo:** la auditoría quedó en un trabajo propio, en 3.13 y con pip y setuptools actualizados; las pruebas siguen en 3.10 y 3.13 ([c:4572201](https://github.com/AndrexxR/Proyecto-Final-Seminario/commit/4572201)).

### Caso 7: el código asumió tres niveles de prioridad y los requisitos piden cuatro

- **Fase:** código (frente a requisitos)
- **Qué propuso la IA:** al implementar HU-03 solo con el documento de diseño, la IA definió `PRIORIDADES = ("Baja", "Media", "Alta")` y lo anotó como supuesto en el README: «El diseño solo muestra `Alta` como ejemplo».
- **Qué estaba mal:** la HU-04 del documento de requisitos ordena los tickets como «Crítica, Media y Baja», así que «Crítica» es un nivel válido. Con el código anterior, un técnico no podía subir un ticket a Crítica: recibía 400.
- **Cómo se detectó:** al preparar este informe, contrastando el documento de requisitos con el código. Se escribieron primero las pruebas desde la HU-04 y 3 fallaron con el código anterior.
- **Qué se hizo:** se agregó `Crítica` a `PRIORIDADES` y la tabla de decisión de la justificación pasó de 12 a 20 combinaciones ([c:740f968](https://github.com/AndrexxR/Proyecto-Final-Seminario/commit/740f968)). Lo que enseña: un supuesto escrito en el README no basta si nadie lo contrasta con los requisitos.

### Caso 8: tres hallazgos de la revisión con IA eran falsos positivos

- **Fase:** código (revisión)
- **Qué propuso la IA:** IA-05 (`usuario=None` lanza `AttributeError`), IA-06 (XSS porque el mensaje de error incluye la prioridad pedida) e IA-08 (`KeyError` en `guardar_cambio_prioridad`).
- **Qué estaba mal:** ninguno es explotable en el flujo real. El contrato exige un `Usuario` ya autenticado. El valor se muestra con `repr` dentro de una respuesta JSON. Y la existencia del ticket se valida antes de guardar.
- **Cómo se detectó:** el script de reproducción ejecutó cada caso y la clasificación quedó con su razón en [`revision_seguridad.md`, sección 3](revision_seguridad.md#3-revisión-con-ia).
- **Qué se hizo:** no se corrigieron. IA-05 quedó como requisito de la futura API (pendiente P-04) y IA-08 quedó documentado en el docstring ([c:d0c7a19](https://github.com/AndrexxR/Proyecto-Final-Seminario/commit/d0c7a19)). Aceptarlos sin verificar habría agregado código defensivo innecesario.

**Otros errores menores de la IA:** en los datos sintéticos, la IA afirmó que los teléfonos con bloque `000` «no se asignan a líneas reales», un dato que no se podía comprobar, y se cambió por «inventados» (bitácora E14). En el diseño de casos, varias cosas que parecían reglas eran interpretaciones; quedaron como ambigüedades A1 a A9 en [`registro_pruebas.md`, sección 1](registro_pruebas.md#1-reglas-y-tablas-de-casos).

## 5. Estado final del sistema

- **Arquitectura:** la decisión de diseño es el ADR-001, una aplicación web cliente-servidor por capas con la API del LLM como servicio externo ([`docs/diseno_S4.pdf`](docs/diseno_S4.pdf), secciones 3 y 4). Lo implementado hasta ahora es el núcleo del «gestor de prioridad» y del «servicio de auditoría» de ese diseño: una biblioteca de Python sin dependencias de ejecución, en tres capas. Están los modelos con sus validaciones ([`incidencias/modelos.py`](incidencias/modelos.py)), la regla de negocio de HU-03 ([`incidencias/prioridad.py`](incidencias/prioridad.py)) y un repositorio en memoria que reemplaza a la base de datos y a la auditoría ([`incidencias/repositorio.py`](incidencias/repositorio.py)). `cambiar_prioridad` recibe el repositorio como parámetro, así que se podrá conectar una base de datos real sin cambiar la regla.
- **Funcionalidades terminadas:** de las 4 historias Must del documento de requisitos, **HU-03** (ajuste manual de prioridad con justificación y auditoría) está terminada y probada. **HU-01** (clasificación automática), **HU-02** (resumen corto) y **HU-04** (lista ordenada por prioridad) no se implementaron. Incluye control de acceso por rol, validación de la justificación (texto, 500 caracteres como máximo, sin saltos de línea ni caracteres de control), bloqueo de tickets cerrados y una demostración por consola (`python -m incidencias`).
- **Pruebas:** 116 pruebas en 4 archivos ([`tests/`](tests/)). Cubren las cuatro funciones con reglas del negocio con particiones, límites y tabla de decisión ([`registro_pruebas.md`](registro_pruebas.md)), y 5 errores introducidos a propósito, todos detectados (registro, sección 3). Pipeline: [ejecuciones en GitHub Actions](https://github.com/AndrexxR/Proyecto-Final-Seminario/actions/workflows/ci.yml).
- **Pendientes:** las historias Must HU-01, HU-02 y HU-04 y las demás (HU-05 a HU-08); la base de datos con consultas con parámetros; la API web (`PATCH /api/tickets/{id}/prioridad`) con autenticación; la integración real con la API del LLM (con su meta de 3 s en el 95 % de las peticiones); la interfaz web; y la guía de despliegue y el plan de operación, que no se hicieron. Quedan además por confirmar con el docente las ambigüedades A2, A3, A7, A8 y A9 y los pendientes P-01 a P-05 de [`revision_seguridad.md`](revision_seguridad.md#4-pendientes).

## 6. Reflexión ética y legal

| Principio | Decisión en mi proyecto | Evidencia |
|---|---|---|
| Datos personales (Ley 1581 de 2012) | La entrevista se grabó y su transcripción se procesó con IA solo con autorización explícita del entrevistado (finalidad informada). El modelo de datos se limitó a lo necesario: `Usuario` tiene `nombre_visible` y rol, sin datos sensibles. El registro de auditoría guarda solo el `usuario_id` del técnico, no su nombre ni su contacto, con una finalidad concreta: la trazabilidad del cambio. La justificación es texto libre y podría recibir datos de clientes; por eso tiene un tope de 500 caracteres y en las pruebas solo hay datos sintéticos. Pendiente antes de usar datos reales: aviso de privacidad, autorización del titular y política de conservación de la auditoría | [`docs/requisitos.pdf`](docs/requisitos.pdf), sección 1; [`docs/diseno_S4.pdf`](docs/diseno_S4.pdf), sección 5; [`RegistroAuditoria`](incidencias/modelos.py); [`tests/datos/datos_sinteticos.json`](tests/datos/datos_sinteticos.json); [`registro_pruebas.md`, sección 4](registro_pruebas.md#4-datos-de-prueba-sintéticos) |
| Sesgo | La IA puede subestimar incidencias de ciertas sedes o escritas en lenguaje informal. El sistema no confía en ella a ciegas: la decisión final es humana y la auditoría guarda la sugerida junto a la final, así que se puede medir en qué casos el técnico corrige a la IA; eso es lo que pide la HU-07 («evaluar el desempeño de la IA»). Ese análisis está pendiente porque no hay datos reales | [`cambiar_prioridad`](incidencias/prioridad.py) nunca modifica `prioridad_sugerida`; prueba `test_corregir_prioridad_conserva_la_sugerencia_original_de_la_ia` |
| Transparencia | La prioridad sugerida por la IA y la decidida por la persona se guardan por separado y la sugerida no se sobrescribe. El uso de IA en el desarrollo está declarado en el README (sección 7), en la bitácora y en los commits (`Co-Authored-By: Claude`) | [README, «Uso de IA»](README.md#7-uso-de-ia); [`bitacora_ia.md`](bitacora_ia.md) |
| Responsabilidad | Del cambio de prioridad responde el técnico, identificado en la auditoría y obligado a justificar cuando se aparta de la IA. Del código respondo yo, aunque lo haya generado una IA: por eso cada hallazgo se verificó antes de aceptarlo. La IA no responde por nada | Casos 3 y 8 de la sección 4; [`revision_seguridad.md`](revision_seguridad.md) |
| Propiedad intelectual y política de uso | Los documentos se redactaron con apoyo de ChatGPT y el código se generó con Claude y Claude Code. La política del curso permite la IA si se declara, y así se hizo. La licencia del proyecto es MIT (README, sección 8). Los datos de prueba son inventados: no se copiaron datos ni textos de terceros | [README, sección 8](README.md#8-autor-y-licencia); [`tests/datos/`](tests/datos/datos_sinteticos.json) |

**Dilema: ¿justificar siempre, o solo cuando el técnico se aparta de la IA?** Exigir justificación en todo cambio da la máxima trazabilidad, pero tiene dos costos. Obliga a escribir texto libre en cada caso, y ese texto puede terminar recogiendo datos personales de clientes («el señor de la tienda…»). Además vuelve la justificación un trámite que se llena con cualquier cosa. No exigirla nunca deja sin explicación justamente los casos en que la persona contradice a la IA. La decisión fue exigirla solo cuando el técnico se aparta de la sugerencia o cuando no hay sugerencia (bitácora E3), y guardar en la auditoría **todos** los cambios, incluidos los que coinciden con la IA. Así se reduce el texto libre (y con él los datos personales) sin perder la posibilidad de detectar el riesgo contrario, el sesgo de automatización: un técnico que acepta siempre lo que dice la IA. Las pruebas `test_volver_a_la_sugerencia_de_la_ia_no_exige_justificacion` y `test_ticket_pendiente_de_clasificacion_exige_justificacion` fijan esta decisión.

## 7. Aprendizajes

**Qué sé hacer ahora.** Escribir una regla de negocio como un contrato verificable, con los errores y su código HTTP. Diseñar casos con particiones, límites y tablas de decisión. Leer una prueba y preguntarme si fallaría al romper el código. Usar un linter con reglas de seguridad. Montar un pipeline de integración continua.

**En qué confié de más en la IA.**
1. En que pruebas en verde son pruebas buenas. El caso 4 muestra 34 pruebas en verde que no detectaban errores evidentes.
2. En que el código de la IA era seguro porque pasaba las pruebas. El caso 3 muestra lo contrario.
3. Sobre todo, en el agente. Le delegué casi todo el trabajo de las últimas fases e integré a `main` los cambios sin leer cada diff (la casilla «Revisar el diff de cada commit» del PR #1 quedó sin marcar). El agente sí verificó, y dejó la evidencia en cada commit, pero la supervisión que la materia pide era mía.

**Qué haría distinto.** Leer cada diff del agente antes de integrarlo y pedirle cambios más pequeños para poder revisarlos. Escribir yo las reglas y las tablas de casos y dejar a la IA solo la generación y la revisión. Guardar desde el principio en el repositorio los documentos de cada módulo y contrastar el código con los requisitos completos, no solo con el diseño: así habría encontrado antes el nivel «Crítica» (caso 7).

## 8. Anexos

- Bitácora de uso de IA: [`bitacora_ia.md`](bitacora_ia.md)
- Revisión de código y seguridad: [`revision_seguridad.md`](revision_seguridad.md) y [`docs/revision_ia.md`](docs/revision_ia.md)
- Registro de pruebas: [`registro_pruebas.md`](registro_pruebas.md)
- Pipeline: [`.github/workflows/ci.yml`](.github/workflows/ci.yml) y [ejecuciones](https://github.com/AndrexxR/Proyecto-Final-Seminario/actions/workflows/ci.yml)
- Diapositivas de la sustentación: [`docs/sustentacion.pdf`](docs/sustentacion.pdf)
- Documento de requisitos (necesidades, historias, MoSCoW y trazabilidad): [`docs/requisitos.pdf`](docs/requisitos.pdf)
- Documento de diseño (matriz, C4, ADR-001, modelo de datos y API): [`docs/diseno_S4.pdf`](docs/diseno_S4.pdf)
- No están en el repositorio: la propuesta del módulo 1, la transcripción de la entrevista, la guía de despliegue y el plan de operación

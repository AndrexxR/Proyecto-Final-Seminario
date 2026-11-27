# Informe final del proyecto integrador

Proyecto: Clasificación y priorización de incidencias con IA (ajuste manual de prioridad, HU-03)  
Estudiante: Carlos Andrés Rueda  
Repositorio: https://github.com/AndrexxR/Proyecto-Final-Seminario  
Fecha: 2026-11-27

## 1. Resumen

El proyecto parte de un sistema web de inventarios en el que los usuarios reportan fallas: el datáfono no conecta, el inventario no cuadra, el lector no reconoce un código. La idea es que una IA lea cada reporte y le sugiera una prioridad al equipo de soporte. El problema es que la IA se puede equivocar, y el cliente fue claro en que la última palabra la tiene el técnico. Por eso construí la historia HU-03: el técnico puede cambiar la prioridad que sugirió la IA, tiene que justificar cuando se aparta de ella y cada cambio queda guardado en una auditoría.

Usé IA en casi todo el proceso: ChatGPT para los requisitos y el diseño, y Claude y Claude Code para el código, las pruebas y el pipeline. De la fase inicial (la propuesta) no guardé evidencia. Lo más valioso fue lo que encontramos al revisar lo que producía la IA: inventó requisitos que nadie pidió, propuso un modelo de datos que perdía la sugerencia original, escribió código que dejaba modificar tickets cerrados y me entregó 34 pruebas en verde que no detectaban errores. Hoy el proyecto tiene 116 pruebas pasando, ruff sin avisos y el pipeline de GitHub Actions en verde.

## 2. Problema y usuario

El usuario principal es el **técnico de soporte**, que atiende las incidencias del sistema de inventarios. También están el usuario operativo, que reporta la falla, y el líder de operaciones, que quiere revisar qué se cambió y por qué ([requisitos, sección 2](docs/requisitos.pdf)).

Hoy el equipo lee los reportes uno por uno para decidir cuál atender primero. En la entrevista con el cliente (un compañero hizo el papel del líder de operaciones; fue el 20/10/2026, duró 18 minutos y se grabó con su autorización) salieron dos frases que resumen el proyecto:

> «Perdemos horas leyendo reportes para saber cuál es urgente y cuál puede esperar» (N-01)
>
> «A veces el sistema sugiere algo pero el técnico debe tener la última palabra» (N-03)

De ahí salieron ocho historias de usuario. Me concentré en la HU-03, que es Must porque es la que garantiza el control humano cuando el modelo falla. La historia y su criterio de aceptación están en el [README](README.md#1-qué-es).

La propuesta del módulo 1 y la transcripción de la entrevista no las tengo en el repositorio; lo que cuento aquí sale del documento de requisitos, que cita la entrevista.

## 3. La IA en el ciclo de vida

Antes de la tabla, una aclaración sobre cómo trabajé. En requisitos y diseño usé ChatGPT para armar borradores que después revisé y corregí ([requisitos, sección 7](docs/requisitos.pdf); [diseño, sección 7](docs/diseno_S4.pdf)). La primera versión del código la hice con Claude en modo chat: copiaba sus respuestas y hacía yo los commits. Desde la revisión de seguridad en adelante trabajé con Claude Code como agente, en la rama `claude/wonderful-cerf-d5iioc`: el agente escribió el código, corrió las verificaciones y dejó cada paso en un commit firmado con `Co-Authored-By: Claude`. Yo le pedía cada tarea y decidía cuándo integrarla a `main`. Lo retomo en la sección 7, porque ahí está uno de mis aprendizajes.

| Módulo y fase | Qué hice con IA | Herramienta | Evidencia (enlace) | Cómo verifiqué |
|---|---|---|---|---|
| 1. Fundamentos | No guardé evidencia de esta fase. El problema y el alcance quedaron en la introducción del documento de requisitos | — | [requisitos, sección 1](docs/requisitos.pdf) | — |
| 2. Requisitos | Pasar la transcripción de la entrevista a historias de usuario, escenarios Gherkin y atributos de calidad | ChatGPT | [requisitos, secciones 4 a 7](docs/requisitos.pdf) | Revisé cada historia con INVEST, exigí una cita textual del cliente por necesidad, quité lo que no tenía cita (caso 1) y cambié palabras como «rápido» por metas con número (3,0 s, 99 %, 25 palabras) |
| 3. Diseño | Matriz de alternativas, diagramas C4, modelo de datos, API y el ADR-001 | ChatGPT | [diseño, secciones 2 a 7](docs/diseno_S4.pdf) | Comparé cada actor, entidad y endpoint con las historias HU-01 a HU-08 y pedí una revisión de coherencia entre las partes; así salió el error del caso 2 |
| 4. Código | Implementar HU-03 a partir del contrato; después, revisión de seguridad y 8 correcciones, una por commit | Claude (chat) y Claude Code (agente) | [76e8596](https://github.com/AndrexxR/Proyecto-Final-Seminario/commit/76e8596), [revision_seguridad.md](revision_seguridad.md), [docs/revision_ia.md](docs/revision_ia.md), bitácora E5 y E7 a E11 | Pruebas, ruff con reglas de seguridad y un script que reproducía cada hallazgo de la IA: 6 eran reales y 3 falsos positivos |
| 5. Pruebas | Pruebas primero (TDD); luego tablas de casos con particiones, límites y tabla de decisión, pruebas con pytest y datos sintéticos | Claude (chat) y Claude Code (agente) | [registro_pruebas.md](registro_pruebas.md), [tests/test_reglas.py](tests/test_reglas.py), [tests/datos](tests/datos/datos_sinteticos.json), bitácora E4 y E12 a E15 | Comparar el borrador de la IA ([37e64b9](https://github.com/AndrexxR/Proyecto-Final-Seminario/commit/37e64b9)) con la versión revisada ([bf12242](https://github.com/AndrexxR/Proyecto-Final-Seminario/commit/bf12242)) y meter 5 errores a propósito en el código |
| 6. Operación | Pipeline de integración continua: ruff, pytest en Python 3.10 y 3.13, y pip-audit | Claude Code (agente) | [ci.yml](.github/workflows/ci.yml), [ejecuciones](https://github.com/AndrexxR/Proyecto-Final-Seminario/actions/workflows/ci.yml), [README, instalación](README.md#3-instalación), bitácora E16 | La primera ejecución falló y hubo que corregirla (caso 6); los comandos del README se probaron en un clon limpio |

## 4. Verificación: lo que la IA hizo mal y cómo lo encontraste

Aquí van los casos en los que la IA se equivocó. Hay de cinco fases distintas: requisitos (caso 1), diseño (2), código (3, 5, 7 y 8), pruebas (4) y operación (6).

### Caso 1: requisitos que el cliente nunca pidió

- **Fase:** requisitos
- **Qué propuso la IA:** cuando le pedí a ChatGPT organizar las historias a partir de la entrevista, agregó «Envío de correos automáticos» y «Asignación automática a técnicos según carga».
- **Qué estaba mal:** nadie pidió eso en la entrevista. Si lo dejaba, el proyecto crecía sin una necesidad real y además empezaba a manejar más datos de las personas (correos, carga de trabajo de cada técnico).
- **Cómo lo detectaste:** me había puesto la regla de que cada necesidad tuviera una cita textual del cliente (tabla N-01 a N-06). Estas dos no tenían ninguna.
- **Qué hiciste:** las quité y lo dejé anotado en la sección 7 del [documento de requisitos](docs/requisitos.pdf). En el diseño también quedaron por fuera ([diseño](docs/diseno_S4.pdf), «correcciones adicionales», punto 5). El documento está en el repositorio desde [6e32e20](https://github.com/AndrexxR/Proyecto-Final-Seminario/commit/6e32e20).

### Caso 2: un modelo de datos que olvidaba lo que dijo la IA

- **Fase:** diseño
- **Qué propuso la IA:** el diseño inicial «podía guardar solo la prioridad actual y perder la sugerencia original», y el primer borrador de contenedores podía «mezclar auditoría con datos operativos» (así quedó anotado en la sección 7 del [documento de diseño](docs/diseno_S4.pdf)).
- **Qué estaba mal:** si al corregir la prioridad se pierde lo que sugirió la IA, ya no se puede saber si la decisión final fue de la IA o del técnico, que es justo lo que pide la N-03, ni evaluar qué tan bien acierta el modelo (HU-07).
- **Cómo lo detectaste:** comparando cada entidad del modelo con las historias HU-03 y HU-07.
- **Qué hiciste:** separé `prioridad_sugerida` de `prioridad_actual`, agregué la entidad `HistorialPrioridad` y saqué la auditoría a su propio almacenamiento. Esa decisión llegó al código: `cambiar_prioridad` nunca toca la prioridad sugerida, y la prueba `test_corregir_prioridad_conserva_la_sugerencia_original_de_la_ia` lo comprueba ([1bacf77](https://github.com/AndrexxR/Proyecto-Final-Seminario/commit/1bacf77)).

### Caso 3: se podía cambiar la prioridad de un ticket cerrado

- **Fase:** código
- **Qué propuso la IA:** en la primera implementación ([76e8596](https://github.com/AndrexxR/Proyecto-Final-Seminario/commit/76e8596)) el bloqueo de tickets cerrados era `if ticket.estado == ESTADO_CERRADO`, con el estado como texto libre.
- **Qué estaba mal:** si el estado llegaba como `"Cerrado"` (con mayúscula) o `" cerrado"` (con un espacio), el ticket no se reconocía como cerrado y aceptaba el cambio. Las 14 pruebas originales pasaban porque todas usaban `"cerrado"` bien escrito.
- **Cómo lo detectaste:** en la revisión de seguridad. La IA lo reportó (hallazgo IA-10) y, antes de creerle, se reprodujo con un script: `IA-10 estado 'Cerrado': sin error -> 'Alta'` ([docs/revision_ia.md](docs/revision_ia.md)).
- **Qué hiciste:** ahora el ticket solo acepta estados de una lista cerrada y lanza `ValueError` con cualquier otro valor, con una prueba nueva ([fe40129](https://github.com/AndrexxR/Proyecto-Final-Seminario/commit/fe40129)). Me quedó una lección: la misma IA que escribió el código encontró el error solo cuando le pedí revisarlo con criterios de seguridad, y las pruebas en verde no lo veían.

### Caso 4: 34 pruebas en verde que no detectaban errores

- **Fase:** pruebas
- **Qué propuso la IA:** le pedí las pruebas a partir de mis reglas y tablas de casos, y entregó un borrador de 34 pruebas, todas pasando ([37e64b9](https://github.com/AndrexxR/Proyecto-Final-Seminario/commit/37e64b9)). Tenía cosas como `pytest.raises(Exception)`, límites calculados con la constante del código (`LONGITUD_MAXIMA_JUSTIFICACION + 1`) y `assert ticket is not None`.
- **Qué estaba mal:** eran pruebas débiles. `Exception` acepta cualquier error, aunque sea otro. Si el esperado sale de la constante del código, cambia junto con el código y nunca falla. Y `is not None` en un objeto recién creado siempre es verdad.
- **Cómo lo detectaste:** ruff marcó la primera con la regla `B017`. Para estar seguros, metimos 5 errores en una copia del código y corrimos el borrador contra cada uno. Con tres de ellos (quitar la validación de tipo, subir el límite de 500 a 5000 y auditar mal la prioridad sugerida), el borrador seguía diciendo «34 passed».
- **Qué hiciste:** se corrigieron con el tipo exacto de error y su código 400, valores fijos (499, 500 y 501), la tabla de combinaciones completa y la comprobación de que un error no deja cambios a medias ([bf12242](https://github.com/AndrexxR/Proyecto-Final-Seminario/commit/bf12242)). La versión revisada detecta los 5 errores. El detalle prueba por prueba está en la [sección 2 del registro de pruebas](registro_pruebas.md#2-revisión-de-las-pruebas-generadas-por-la-ia).

### Caso 5: una validación más estricta que la regla

- **Fase:** código (lo encontró una prueba)
- **Qué propuso la IA:** para que nadie pudiera meter saltos de línea falsos en la auditoría, la IA usó `isprintable()` para validar la justificación ([189e2f6](https://github.com/AndrexxR/Proyecto-Final-Seminario/commit/189e2f6)).
- **Qué estaba mal:** la regla solo prohíbe saltos de línea y caracteres de control, pero `isprintable()` también rechaza el espacio no separable, el que aparece cuando uno copia texto de Word o de un correo. Un técnico que pegara «Caja 2 bloqueada» desde un correo iba a recibir un error sin entender por qué.
- **Cómo lo detectaste:** con una prueba escrita desde la regla y no desde el código (fila F1-P7 del registro). Falló, y antes de tocarla se volvió a leer la regla: el que estaba mal era el código.
- **Qué hiciste:** se corrigió el código, no la prueba. Ahora solo se rechazan los caracteres de control y los separadores de línea ([46aff6a](https://github.com/AndrexxR/Proyecto-Final-Seminario/commit/46aff6a)).

### Caso 6: el primer pipeline salió en rojo

- **Fase:** operación
- **Qué propuso la IA:** un pipeline que corría `pip-audit` en todas las versiones de Python ([56cd73a](https://github.com/AndrexxR/Proyecto-Final-Seminario/commit/56cd73a)).
- **Qué estaba mal:** `pip-audit` sin argumentos revisa todo lo que está instalado en el servidor, no solo el proyecto. En Python 3.10 encontró vulnerabilidades en `setuptools` y `filelock`, que no son dependencias del proyecto: el proyecto no tiene ninguna.
- **Cómo lo detectaste:** la primera ejecución en GitHub Actions. Ruff y las pruebas pasaron, pero el paso de auditoría falló solo en 3.10, y el log mostraba qué paquetes eran.
- **Qué hiciste:** la auditoría pasó a un trabajo aparte, con Python 3.13 y pip y setuptools actualizados; las pruebas siguen en las dos versiones ([4572201](https://github.com/AndrexxR/Proyecto-Final-Seminario/commit/4572201)).

### Caso 7: faltaba el nivel «Crítica»

- **Fase:** código, comparado con los requisitos
- **Qué propuso la IA:** al implementar HU-03 a partir del documento de diseño, la IA definió tres niveles (`Baja`, `Media`, `Alta`) y lo dejó como supuesto en el README: «el diseño solo muestra Alta como ejemplo».
- **Qué estaba mal:** la HU-04 del documento de requisitos ordena los tickets como «Crítica, Media y Baja», así que «Crítica» tenía que existir. Con el código anterior, nadie podía subir un ticket a Crítica.
- **Cómo lo detectaste:** al preparar este informe comparé el documento de requisitos con el código. Primero se escribieron las pruebas a partir de la HU-04, y 3 fallaron.
- **Qué hiciste:** se agregó `Crítica` y la tabla de combinaciones de la justificación pasó de 12 a 20 casos ([740f968](https://github.com/AndrexxR/Proyecto-Final-Seminario/commit/740f968)). Lo que aprendí: un supuesto anotado en el README no sirve de mucho si nadie lo compara con los requisitos.

### Caso 8: tres alarmas de seguridad que no eran reales

- **Fase:** código (revisión)
- **Qué propuso la IA:** en la revisión de seguridad marcó tres problemas: que `usuario=None` rompía la función (IA-05), un posible XSS porque el mensaje de error muestra la prioridad pedida (IA-06) y un `KeyError` al guardar (IA-08).
- **Qué estaba mal:** en el flujo real ninguno se puede dar. El usuario siempre llega autenticado, el valor se muestra escapado en una respuesta JSON y el ticket se valida antes de guardar.
- **Cómo lo detectaste:** el mismo script de reproducción ejecutó cada caso. La razón de cada uno quedó en la [sección 3 del informe de seguridad](revision_seguridad.md#3-revisión-con-ia).
- **Qué hiciste:** no se corrigieron, porque habría sido meter código defensivo que no hace falta. IA-05 quedó anotado como requisito para cuando exista la API, e IA-08 quedó documentado en el docstring ([d0c7a19](https://github.com/AndrexxR/Proyecto-Final-Seminario/commit/d0c7a19)).

Hubo otros errores más pequeños. Al generar los datos de prueba, la IA afirmó que los teléfonos con `000` «no se asignan a líneas reales», algo que no se podía comprobar, y se cambió por «inventados» (bitácora E14). Y al diseñar los casos, varias cosas que parecían reglas eran en realidad interpretaciones; quedaron anotadas como ambigüedades A1 a A9 en el [registro de pruebas](registro_pruebas.md#1-reglas-y-tablas-de-casos).

## 5. Estado final del sistema

- **Arquitectura:** en el diseño elegí una aplicación web cliente-servidor por capas, con la API del LLM como servicio externo (ADR-001, 96 de 110 puntos en la matriz; [diseño, secciones 3 y 4](docs/diseno_S4.pdf)). De esa arquitectura está hecho el núcleo del gestor de prioridad y de la auditoría, en Python y sin dependencias. Son tres partes: los modelos con sus validaciones ([modelos.py](incidencias/modelos.py)), la regla de HU-03 ([prioridad.py](incidencias/prioridad.py)) y un repositorio en memoria que por ahora hace de base de datos ([repositorio.py](incidencias/repositorio.py)). Como `cambiar_prioridad` recibe el repositorio por parámetro, más adelante se puede conectar una base de datos real sin tocar la regla.
- **Funcionalidades terminadas:** de las cuatro historias Must, la **HU-03** está terminada y probada: control de acceso por rol, justificación obligatoria cuando el técnico se aparta de la IA (máximo 500 caracteres, sin saltos de línea), bloqueo de tickets cerrados, auditoría de cada cambio y una demostración por consola (`python -m incidencias`). La HU-01 (clasificación automática), la HU-02 (resumen) y la HU-04 (lista ordenada) no alcancé a hacerlas.
- **Pruebas:** 116 pruebas en 4 archivos ([tests](tests/)), que cubren las cuatro funciones con reglas de negocio. Las tablas de casos están en el [registro de pruebas](registro_pruebas.md). Los 5 errores metidos a propósito los detectaron las pruebas. Última ejecución del pipeline: [GitHub Actions](https://github.com/AndrexxR/Proyecto-Final-Seminario/actions/workflows/ci.yml).
- **Pendientes:** las historias HU-01, HU-02 y HU-04, y de la HU-05 a la HU-08; la base de datos (con consultas con parámetros); la API web con autenticación; la conexión real con el LLM y su meta de 3 segundos; la interfaz; y la guía de despliegue y el plan de operación, que no hice. También quedan preguntas para el docente: las ambigüedades A2, A3, A7, A8 y A9 del registro de pruebas y los pendientes P-01 a P-05 del [informe de seguridad](revision_seguridad.md#4-pendientes).

## 6. Reflexión ética y legal

| Principio | Decisión en mi proyecto | Evidencia |
|---|---|---|
| Datos personales (Ley 1581 de 2012) | La entrevista se grabó y se procesó con IA solo con autorización del entrevistado. En el modelo de datos dejé lo mínimo: el usuario tiene un nombre visible y un rol, nada sensible. La auditoría guarda el `usuario_id` del técnico, no su nombre ni su teléfono, y solo para saber quién hizo el cambio. Como la justificación es texto libre y alguien podría escribir datos de un cliente, le puse un máximo de 500 caracteres, y en las pruebas solo uso datos inventados. Antes de usar datos reales faltan el aviso de privacidad, la autorización de los titulares y definir cuánto tiempo se guarda la auditoría | [requisitos, sección 1](docs/requisitos.pdf); [diseño, sección 5](docs/diseno_S4.pdf); [modelos.py](incidencias/modelos.py); [datos sintéticos](tests/datos/datos_sinteticos.json) |
| Sesgo | La IA podría subestimar reportes de ciertas sedes o escritos de manera informal. Por eso la decisión final es del técnico y la auditoría guarda la prioridad sugerida al lado de la final: así se puede medir en qué casos la gente corrige a la IA, que es lo que pide la HU-07. Ese análisis queda pendiente porque todavía no hay datos reales | [prioridad.py](incidencias/prioridad.py) nunca modifica la sugerida; prueba `test_corregir_prioridad_conserva_la_sugerencia_original_de_la_ia` |
| Transparencia | En el sistema siempre se puede ver qué sugirió la IA y qué decidió la persona, porque se guardan por separado. En el desarrollo, el uso de IA está declarado en el README, en la bitácora y en los commits | [README, uso de IA](README.md#7-uso-de-ia); [bitácora](bitacora_ia.md) |
| Responsabilidad | Del cambio de prioridad responde el técnico: queda en la auditoría con su justificación. Del código respondo yo, aunque lo haya escrito una IA; por eso cada hallazgo se comprobó antes de aceptarlo o descartarlo | Casos 3 y 8; [revision_seguridad.md](revision_seguridad.md) |
| Propiedad intelectual y política de uso | Los documentos los redacté con apoyo de ChatGPT y el código se hizo con Claude y Claude Code. El curso permite usar IA si se declara, y así lo hice. La licencia del proyecto es MIT. Los datos de prueba son inventados; no copié datos ni textos de terceros | [README, autor y licencia](README.md#8-autor-y-licencia); [datos sintéticos](tests/datos/datos_sinteticos.json) |

**El dilema que más me hizo pensar fue si pedir justificación en todos los cambios o solo en algunos.** Pedirla siempre parecía lo más seguro, pero tenía dos problemas. Se volvía un trámite que la gente llena con cualquier cosa, y más texto libre significa más riesgo de que alguien escriba datos de un cliente («el señor de la tienda dijo…»). No pedirla nunca dejaba sin explicación justo los casos importantes, cuando una persona contradice a la IA. Decidí pedirla solo cuando el técnico se aparta de lo que sugirió la IA (o cuando no hay sugerencia), pero guardar en la auditoría **todos** los cambios, también los que coinciden con la IA. Así hay menos texto libre y sigo pudiendo detectar el riesgo contrario: un técnico que acepta todo lo que dice la IA sin pensarlo (bitácora E3). Las pruebas `test_volver_a_la_sugerencia_de_la_ia_no_exige_justificacion` y `test_ticket_pendiente_de_clasificacion_exige_justificacion` dejan fija esta decisión.

## 7. Aprendizajes

Al empezar el seminario no sabía escribir una regla de negocio como un contrato con sus errores, ni diseñar casos de prueba con particiones, límites y tablas de decisión. Ahora sé hacerlo, y también configurar un linter con reglas de seguridad y montar un pipeline en GitHub Actions. Lo que más me cambió fue la costumbre de preguntarme, frente a cada prueba, si fallaría en caso de que el código estuviera mal.

Confié de más en la IA en tres cosas:

1. **Creí que pruebas en verde eran pruebas buenas.** El caso 4 muestra lo contrario: 34 pruebas en verde que no detectaban errores evidentes.
2. **Creí que si el código pasaba las pruebas, era seguro.** El caso 3 demuestra que no.
3. **Confié demasiado en el agente.** En las últimas fases le delegué casi todo e integré sus cambios a `main` sin leer cada diff (en el primer pull request la casilla «revisar el diff de cada commit» quedó sin marcar). El agente sí verificó y dejó la evidencia en cada commit, pero supervisarlo me tocaba a mí, y es justo lo que pide la materia.

Si lo volviera a hacer, leería cada cambio del agente antes de integrarlo y le pediría cambios más pequeños para poder revisarlos de verdad. También escribiría yo las reglas y las tablas de casos, y dejaría a la IA generar y revisar. Y guardaría desde el principio todos los documentos en el repositorio, comparando el código con los requisitos completos y no solo con el diseño; así habría encontrado mucho antes lo de «Crítica» (caso 7).

## 8. Anexos

- Bitácora de uso de IA: [bitacora_ia.md](bitacora_ia.md)
- Documento de requisitos: [docs/requisitos.pdf](docs/requisitos.pdf)
- Documento de diseño: [docs/diseno_S4.pdf](docs/diseno_S4.pdf)
- Revisión de código y seguridad: [revision_seguridad.md](revision_seguridad.md) y [docs/revision_ia.md](docs/revision_ia.md)
- Registro de pruebas: [registro_pruebas.md](registro_pruebas.md)
- Pipeline: [ci.yml](.github/workflows/ci.yml) y [ejecuciones](https://github.com/AndrexxR/Proyecto-Final-Seminario/actions/workflows/ci.yml)
- Diapositivas de la sustentación: [docs/sustentacion.pdf](docs/sustentacion.pdf)
- No están en el repositorio: la propuesta del módulo 1, la transcripción de la entrevista, la guía de despliegue y el plan de operación

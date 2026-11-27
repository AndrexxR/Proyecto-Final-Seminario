"""Pruebas de las reglas de HU-03 a partir de las tablas de registro_pruebas.md.

Los esperados son valores fijos sacados de la regla escrita en el registro
(sección 1), no de las constantes del código.
"""
from datetime import datetime, timezone

import pytest

from incidencias.modelos import (
    ConflictoError,
    JustificacionInvalidaError,
    JustificacionRequeridaError,
    PermisoDenegadoError,
    PrioridadInvalidaError,
    RegistroAuditoria,
    Ticket,
    TicketNoEncontradoError,
    Usuario,
)
from incidencias.prioridad import (
    _exige_justificacion,
    _normalizar_justificacion,
    cambiar_prioridad,
)
from incidencias.repositorio import RepositorioEnMemoria

AHORA = datetime(2026, 11, 21, 8, 15, tzinfo=timezone.utc)
TECNICO = Usuario(usuario_id=7, rol="soporte")


# ---------- F1. _normalizar_justificacion ----------

@pytest.mark.parametrize(
    "entrada, esperado",
    [
        (None, None),  # F1-P1 ausente
        ("", None),  # F1-P2 vacía (también F1-L1: 0 caracteres útiles)
        ("   ", None),  # F1-P3 solo espacios
        ("Afecta el cierre de caja", "Afecta el cierre de caja"),  # F1-P4 válida
        ("  Afecta caja  ", "Afecta caja"),  # F1-P5 se quitan los espacios de los extremos
        (
            "Señal débil en la sede de D'Artagnan, ¿urgente?",
            "Señal débil en la sede de D'Artagnan, ¿urgente?",
        ),  # F1-P6 tildes, ñ, apóstrofo y signos se conservan
        ("Caja 2 bloqueada", "Caja 2 bloqueada"),  # F1-P7 espacio no separable (A5)
        ("Reinicié el servidor\n", "Reinicié el servidor"),  # A3 salto final se quita
        ("x", "x"),  # F1-L2 primer valor válido: 1 caracter
    ],
)
def test_normalizar_justificacion_acepta_y_limpia(entrada, esperado):
    assert _normalizar_justificacion(entrada) == esperado


@pytest.mark.parametrize(
    "entrada",
    [
        12345,  # F1-P8 número
        ["Afecta caja"],  # F1-P8 lista
        {"motivo": "x"},  # F1-P8 diccionario
        "línea 1\nlínea 2",  # F1-P9 salto de línea en medio
        "a\rb",  # F1-P9 retorno de carro en medio
        "a\u2028b",  # F1-P9 separador de línea de Unicode
        "a\u2029b",  # F1-P9 separador de párrafo de Unicode
        "a\x00b",  # F1-P10 caracter nulo
        "a\x1b[2Jb",  # F1-P10 secuencia de escape de terminal
        "a\tb",  # F1-P10 tabulador (A4: es de control)
        "x" * 501,  # F1-L4 primer valor inválido: 501 caracteres
        "x" * 600,  # F1-P11 bastante más largo que el máximo
    ],
)
def test_normalizar_justificacion_rechaza_con_error_400(entrada):
    with pytest.raises(JustificacionInvalidaError) as error:
        _normalizar_justificacion(entrada)
    assert error.value.codigo_http == 400


@pytest.mark.parametrize(
    "entrada, esperado",
    [
        ("x" * 500, "x" * 500),  # F1-L3 último valor válido: 500 caracteres
        ("  " + "x" * 500 + "  ", "x" * 500),  # F1-L5 500 útiles con espacios en los extremos (A2)
        ("x" * 499, "x" * 499),  # justo debajo del máximo
    ],
)
def test_normalizar_justificacion_en_el_limite_de_500(entrada, esperado):
    assert _normalizar_justificacion(entrada) == esperado


# ---------- F2. Ticket ----------

@pytest.mark.parametrize(
    "estado, sugerida, actual",
    [
        ("abierto", "Media", "Media"),  # F2-P1 primer estado de la lista
        ("pendiente_clasificacion", None, None),  # F2-P1 y F2-P5 sin análisis de la IA
        ("cerrado", "Alta", "Baja"),  # F2-P1 último estado; F2-P6 primera y última prioridad
        ("abierto", "Baja", None),  # F2-P5 vigente aún sin asignar
    ],
)
def test_ticket_valido_conserva_sus_datos(estado, sugerida, actual):
    ticket = Ticket(1, estado, sugerida, actual)
    assert (ticket.estado, ticket.prioridad_sugerida, ticket.prioridad_actual) == (
        estado,
        sugerida,
        actual,
    )


@pytest.mark.parametrize(
    "estado",
    [
        "Cerrado",  # F2-P2 capitalización
        "ABIERTO",  # F2-P2 todo en mayúsculas
        " cerrado",  # F2-P3 espacio al inicio
        "abierto ",  # F2-P3 espacio al final
        "borrado",  # F2-P4 fuera de la lista
        "",  # F2-P4 vacío
        None,  # F2-P4 sin estado
    ],
)
def test_ticket_con_estado_invalido_lanza_value_error(estado):
    with pytest.raises(ValueError):
        Ticket(1, estado, "Media", "Media")


@pytest.mark.parametrize(
    "sugerida, actual",
    [
        ("alta", "Media"),  # F2-P7 sugerida en minúscula
        ("Urgente", "Media"),  # F2-P7 sugerida fuera de la lista
        ("", "Media"),  # F2-P7 sugerida vacía
        ("Media", "alta"),  # F2-P8 vigente en minúscula
        ("Media", "Urgente"),  # F2-P8 vigente fuera de la lista
        ("Media", ""),  # F2-P8 vigente vacía
    ],
)
def test_ticket_con_prioridad_invalida_lanza_value_error(sugerida, actual):
    with pytest.raises(ValueError):
        Ticket(1, "abierto", sugerida, actual)


# ---------- F3. _exige_justificacion: tabla completa ----------

@pytest.mark.parametrize(
    "sugerida, nueva, esperado",
    [
        (None, "Baja", True),  # sin sugerencia: siempre exige
        (None, "Media", True),  # sin sugerencia: siempre exige
        (None, "Alta", True),  # sin sugerencia: siempre exige
        ("Baja", "Baja", False),  # coincide con la sugerida
        ("Baja", "Media", True),  # se aparta hacia arriba
        ("Baja", "Alta", True),  # se aparta hacia arriba
        ("Media", "Baja", True),  # se aparta hacia abajo
        ("Media", "Media", False),  # coincide con la sugerida
        ("Media", "Alta", True),  # se aparta hacia arriba
        ("Alta", "Baja", True),  # se aparta hacia abajo
        ("Alta", "Media", True),  # se aparta hacia abajo
        ("Alta", "Alta", False),  # coincide con la sugerida
        (None, "Crítica", True),  # sin sugerencia: siempre exige
        ("Baja", "Crítica", True),  # se aparta hacia arriba
        ("Media", "Crítica", True),  # se aparta hacia arriba
        ("Alta", "Crítica", True),  # se aparta hacia arriba
        ("Crítica", "Baja", True),  # se aparta hacia abajo
        ("Crítica", "Media", True),  # se aparta hacia abajo
        ("Crítica", "Alta", True),  # se aparta hacia abajo
        ("Crítica", "Crítica", False),  # coincide con la sugerida
    ],
)
def test_exige_justificacion_segun_la_sugerencia(sugerida, nueva, esperado):
    ticket = Ticket(1, "abierto", sugerida, None)
    assert _exige_justificacion(ticket, nueva) is esperado


# ---------- F4. cambiar_prioridad: tabla de decisión ----------

def repo_con(estado="abierto", sugerida="Media", actual="Media"):
    return RepositorioEnMemoria([Ticket(1, estado, sugerida, actual)])


@pytest.mark.parametrize(
    "rol, ticket_id, estado, sugerida, actual, nueva, justificacion, error, codigo",
    [
        # R1: sin permiso; lo demás no importa, aunque también esté mal
        ("operativo", 999, "cerrado", "Media", "Media", "Urgente", None, PermisoDenegadoError, 403),
        # R2: técnico, prioridad fuera de la lista, aunque el ticket no exista (A1)
        ("soporte", 999, "abierto", "Media", "Media", "Urgente", "x", PrioridadInvalidaError, 400),
        # R3: técnico, prioridad válida, ticket inexistente
        ("soporte", 999, "abierto", "Media", "Media", "Alta", "x", TicketNoEncontradoError, 404),
        # R4: ticket cerrado
        ("soporte", 1, "cerrado", "Media", "Media", "Alta", "x", ConflictoError, 409),
        # R5: la prioridad pedida ya es la vigente
        ("soporte", 1, "abierto", "Media", "Alta", "Alta", "x", ConflictoError, 409),
        # R5: también con el ticket pendiente de clasificación (lo agregué por el error M4)
        ("soporte", 1, "pendiente_clasificacion", None, "Alta", "Alta", "x", ConflictoError, 409),
        # R6: se aparta de la sugerida y no hay justificación
        ("soporte", 1, "abierto", "Media", "Media", "Alta", None, JustificacionRequeridaError, 400),
        # R6: sin sugerencia de la IA y con justificación de solo espacios
        (
            "soporte", 1, "pendiente_clasificacion", None, None, "Baja", "   ",
            JustificacionRequeridaError, 400,
        ),
    ],
)
def test_cambiar_prioridad_rechaza_sin_dejar_cambios(
    rol, ticket_id, estado, sugerida, actual, nueva, justificacion, error, codigo
):
    repo = repo_con(estado=estado, sugerida=sugerida, actual=actual)
    with pytest.raises(error) as capturado:
        cambiar_prioridad(repo, ticket_id, nueva, Usuario(3, rol), justificacion, ahora=AHORA)
    assert capturado.value.codigo_http == codigo
    assert repo.obtener_ticket(1).prioridad_actual == actual
    assert repo.auditoria == []


@pytest.mark.parametrize(
    "sugerida, actual, nueva, justificacion, guardada",
    [
        # R7: se aparta de la sugerida, con justificación
        ("Media", "Media", "Alta", "Afecta el cierre de caja", "Afecta el cierre de caja"),
        # R7: sin sugerencia de la IA, con justificación (se guarda sin espacios)
        (None, None, "Alta", "  Caja 3 sin servicio  ", "Caja 3 sin servicio"),
        # R8: vuelve a la sugerida, sin justificación
        ("Media", "Baja", "Media", None, None),
        # R8: vuelve a la sugerida, justificación de solo espacios cuenta como ausente
        ("Alta", "Media", "Alta", "   ", None),
        # R9: vuelve a la sugerida, con justificación opcional
        ("Media", "Baja", "Media", "Lo confirma el cliente", "Lo confirma el cliente"),
    ],
)
def test_cambiar_prioridad_aplica_el_cambio_y_audita(
    sugerida, actual, nueva, justificacion, guardada
):
    repo = repo_con(sugerida=sugerida, actual=actual)
    registro = cambiar_prioridad(repo, 1, nueva, TECNICO, justificacion, ahora=AHORA)

    esperado = RegistroAuditoria(
        ticket_id=1,
        usuario_id=7,
        prioridad_anterior=actual,
        prioridad_sugerida=sugerida,
        prioridad_final=nueva,
        justificacion=guardada,
        fecha_cambio=AHORA,
    )
    assert registro == esperado
    assert repo.auditoria == [esperado]
    ticket = repo.obtener_ticket(1)
    assert (ticket.prioridad_actual, ticket.prioridad_sugerida) == (nueva, sugerida)


def test_cambiar_prioridad_rechaza_justificacion_opcional_invalida():
    # A6: coincide con la sugerida (justificación opcional), pero la que llega no es texto
    repo = repo_con(sugerida="Media", actual="Baja")
    with pytest.raises(JustificacionInvalidaError):
        cambiar_prioridad(repo, 1, "Media", TECNICO, 12345, ahora=AHORA)
    assert repo.auditoria == []


# ---------- Nivel «Crítica» (SRS, HU-04: «orden estricto: Crítica, Media y Baja») ----------

@pytest.mark.parametrize(
    "sugerida, actual, nueva, justificacion",
    [
        ("Alta", "Alta", "Crítica", "Caja bloqueada en quincena"),  # sube a Crítica, se aparta
        ("Crítica", "Alta", "Crítica", None),  # vuelve a la sugerida Crítica, sin justificación
        ("Crítica", "Crítica", "Media", "Era una consulta menor"),  # baja desde Crítica
    ],
)
def test_critica_es_una_prioridad_valida(sugerida, actual, nueva, justificacion):
    repo = repo_con(sugerida=sugerida, actual=actual)
    registro = cambiar_prioridad(repo, 1, nueva, TECNICO, justificacion, ahora=AHORA)
    assert (registro.prioridad_anterior, registro.prioridad_final) == (actual, nueva)
    assert repo.obtener_ticket(1).prioridad_actual == nueva


@pytest.mark.parametrize(
    "invalida",
    [
        "critica",  # sin tilde y en minúscula
        "Critica",  # sin tilde
        "CRÍTICA",  # mayúsculas
    ],
)
def test_critica_mal_escrita_se_rechaza(invalida):
    with pytest.raises(PrioridadInvalidaError):
        cambiar_prioridad(repo_con(), 1, invalida, TECNICO, "x", ahora=AHORA)

"""Pruebas de las reglas de HU-03 a partir de las tablas de registro_pruebas.md."""
from datetime import datetime, timezone

import pytest

from incidencias.modelos import (
    LONGITUD_MAXIMA_JUSTIFICACION,
    ConflictoError,
    JustificacionInvalidaError,
    JustificacionRequeridaError,
    PermisoDenegadoError,
    PrioridadInvalidaError,
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
        ("", None),  # F1-P2 vacía
        ("   ", None),  # F1-P3 solo espacios
        ("Afecta el cierre de caja", "Afecta el cierre de caja"),  # F1-P4 válida
        ("  Afecta caja  ", "Afecta caja"),  # F1-P5 espacios en los extremos
    ],
)
def test_normalizar_justificacion_validas(entrada, esperado):
    assert _normalizar_justificacion(entrada) == esperado


@pytest.mark.parametrize(
    "entrada",
    [
        12345,  # F1-P8 no es texto
        "línea 1\nlínea 2",  # F1-P9 salto de línea
        "a\x00b",  # F1-P10 caracter de control
        "x" * (LONGITUD_MAXIMA_JUSTIFICACION + 1),  # F1-L4 uno más que el máximo
    ],
)
def test_normalizar_justificacion_invalidas(entrada):
    with pytest.raises(Exception):
        _normalizar_justificacion(entrada)


def test_normalizar_justificacion_en_el_maximo():
    texto = "x" * LONGITUD_MAXIMA_JUSTIFICACION  # F1-L3
    assert _normalizar_justificacion(texto) == texto


# ---------- F2. Ticket ----------

@pytest.mark.parametrize(
    "estado",
    [
        "abierto",  # F2-P1 primero de la lista
        "pendiente_clasificacion",  # F2-P1
        "cerrado",  # F2-P1 último de la lista
    ],
)
def test_ticket_con_estado_valido_se_crea(estado):
    ticket = Ticket(1, estado, "Media", "Media")
    assert ticket is not None


@pytest.mark.parametrize(
    "estado",
    [
        "Cerrado",  # F2-P2 capitalización
        " cerrado",  # F2-P3 espacio
        "borrado",  # F2-P4 fuera de la lista
        "",  # F2-P4 vacío
    ],
)
def test_ticket_con_estado_invalido_se_rechaza(estado):
    with pytest.raises(ValueError):
        Ticket(1, estado, "Media", "Media")


@pytest.mark.parametrize(
    "sugerida, actual",
    [
        ("alta", "Media"),  # F2-P7 sugerida en minúscula
        ("Urgente", "Media"),  # F2-P7 sugerida fuera de la lista
        ("Media", "alta"),  # F2-P8 vigente en minúscula
        ("Media", ""),  # F2-P8 vigente vacía
    ],
)
def test_ticket_con_prioridad_invalida_se_rechaza(sugerida, actual):
    with pytest.raises(ValueError):
        Ticket(1, "abierto", sugerida, actual)


# ---------- F3. _exige_justificacion ----------

@pytest.mark.parametrize(
    "sugerida, nueva, esperado",
    [
        (None, "Alta", True),  # sin sugerencia: siempre exige
        ("Media", "Media", False),  # coincide con la sugerida
        ("Media", "Alta", True),  # se aparta de la sugerida
        ("Media", "Baja", True),  # se aparta hacia abajo
    ],
)
def test_exige_justificacion(sugerida, nueva, esperado):
    ticket = Ticket(1, "abierto", sugerida, None)
    assert _exige_justificacion(ticket, nueva) == esperado


# ---------- F4. cambiar_prioridad: tabla de decisión ----------

def repo_con(estado="abierto", sugerida="Media", actual="Media"):
    return RepositorioEnMemoria([Ticket(1, estado, sugerida, actual)])


@pytest.mark.parametrize(
    "usuario, ticket_id, estado, actual, nueva, justificacion, error",
    [
        (Usuario(3, "operativo"), 1, "abierto", "Media", "Alta", "x", PermisoDenegadoError),  # R1
        (TECNICO, 1, "abierto", "Media", "Urgente", "x", PrioridadInvalidaError),  # R2
        (TECNICO, 999, "abierto", "Media", "Alta", "x", TicketNoEncontradoError),  # R3
        (TECNICO, 1, "cerrado", "Media", "Alta", "x", ConflictoError),  # R4
        (TECNICO, 1, "abierto", "Alta", "Alta", "x", ConflictoError),  # R5
        (TECNICO, 1, "abierto", "Media", "Alta", None, JustificacionRequeridaError),  # R6
    ],
)
def test_cambiar_prioridad_errores(usuario, ticket_id, estado, actual, nueva, justificacion, error):
    repo = repo_con(estado=estado, actual=actual)
    with pytest.raises(error):
        cambiar_prioridad(repo, ticket_id, nueva, usuario, justificacion, ahora=AHORA)


@pytest.mark.parametrize(
    "sugerida, actual, nueva, justificacion",
    [
        ("Media", "Media", "Alta", "Afecta el cierre de caja"),  # R7 se aparta, con justificación
        ("Media", "Baja", "Media", None),  # R8 coincide, sin justificación
        ("Media", "Baja", "Media", "Lo confirma el cliente"),  # R9 coincide, con justificación
    ],
)
def test_cambiar_prioridad_exitoso(sugerida, actual, nueva, justificacion):
    repo = repo_con(sugerida=sugerida, actual=actual)
    registro = cambiar_prioridad(repo, 1, nueva, TECNICO, justificacion, ahora=AHORA)
    assert repo.obtener_ticket(1).prioridad_actual == nueva
    assert registro.justificacion == justificacion
    assert len(repo.auditoria) == 1

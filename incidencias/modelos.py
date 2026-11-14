"""Modelos y errores del dominio de incidencias (solo lo necesario para HU-03)."""
from dataclasses import dataclass
from datetime import datetime

# Supuestos de diseño (ver README, sección «Supuestos»):
# el documento S4 no lista los niveles de prioridad ni los estados.
PRIORIDADES = ("Baja", "Media", "Alta")
ROL_SOPORTE = "soporte"
ESTADO_CERRADO = "cerrado"


@dataclass
class Usuario:
    usuario_id: int
    rol: str  # "operativo" | "soporte" | "líder"


@dataclass
class Ticket:
    ticket_id: int
    estado: str
    prioridad_sugerida: str | None  # resultado de la IA; None si el análisis está pendiente
    prioridad_actual: str | None  # valor vigente


@dataclass(frozen=True)
class RegistroAuditoria:
    ticket_id: int
    usuario_id: int
    prioridad_anterior: str | None
    prioridad_sugerida: str | None
    prioridad_final: str
    justificacion: str | None
    fecha_cambio: datetime


class ErrorDePrioridad(Exception):
    """Base de los errores de HU-03. `codigo_http` indica el código de la API."""

    codigo_http = 500


class PrioridadInvalidaError(ErrorDePrioridad):
    codigo_http = 400


class JustificacionRequeridaError(ErrorDePrioridad):
    codigo_http = 400


class PermisoDenegadoError(ErrorDePrioridad):
    codigo_http = 403


class TicketNoEncontradoError(ErrorDePrioridad):
    codigo_http = 404


class ConflictoError(ErrorDePrioridad):
    codigo_http = 409

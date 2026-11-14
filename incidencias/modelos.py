"""Modelos y errores del dominio de incidencias (solo lo necesario para HU-03)."""
from dataclasses import dataclass
from datetime import datetime

# Supuestos de diseño (ver README, sección «Supuestos»):
# el documento S4 no lista los niveles de prioridad ni los estados.
PRIORIDADES = ("Baja", "Media", "Alta")
ROL_SOPORTE = "soporte"
ESTADO_ABIERTO = "abierto"
ESTADO_PENDIENTE_CLASIFICACION = "pendiente_clasificacion"
ESTADO_CERRADO = "cerrado"
ESTADOS = (ESTADO_ABIERTO, ESTADO_PENDIENTE_CLASIFICACION, ESTADO_CERRADO)


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

    def __post_init__(self) -> None:
        """Rechaza estados y prioridades fuera de las listas.

        Sin esta validación, un estado como "Cerrado" o " cerrado" no se reconocía
        como cerrado y el ticket aceptaba cambios (hallazgo H-01).

        Raises:
            ValueError: si `estado` no está en ESTADOS, o si una prioridad no es None
                ni está en PRIORIDADES.
        """
        if self.estado not in ESTADOS:
            raise ValueError(f"Estado de ticket inválido: {self.estado!r}")
        for prioridad in (self.prioridad_sugerida, self.prioridad_actual):
            if prioridad is not None and prioridad not in PRIORIDADES:
                raise ValueError(f"Prioridad de ticket inválida: {prioridad!r}")


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


class JustificacionInvalidaError(ErrorDePrioridad):
    """La justificación no es texto, es demasiado larga o tiene caracteres de control."""

    codigo_http = 400


class PermisoDenegadoError(ErrorDePrioridad):
    codigo_http = 403


class TicketNoEncontradoError(ErrorDePrioridad):
    codigo_http = 404


class ConflictoError(ErrorDePrioridad):
    codigo_http = 409

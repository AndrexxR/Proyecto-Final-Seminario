"""Modelos, constantes y errores del dominio de incidencias (lo necesario para HU-03)."""
from dataclasses import dataclass
from datetime import datetime

# Supuestos de diseño (ver README, sección «Supuestos»):
# el documento S4 no lista los niveles de prioridad ni los estados.
PRIORIDADES = ("Baja", "Media", "Alta", "Crítica")
ROL_SOPORTE = "soporte"
ESTADO_ABIERTO = "abierto"
ESTADO_PENDIENTE_CLASIFICACION = "pendiente_clasificacion"
ESTADO_CERRADO = "cerrado"
ESTADOS = (ESTADO_ABIERTO, ESTADO_PENDIENTE_CLASIFICACION, ESTADO_CERRADO)
# Límite de la justificación guardada en la auditoría (supuesto; el diseño S4 no lo fija).
LONGITUD_MAXIMA_JUSTIFICACION = 500


@dataclass
class Usuario:
    """Usuario autenticado que hace la petición. `rol` decide qué puede hacer."""

    usuario_id: int
    rol: str  # "operativo" | "soporte" | "líder"


@dataclass
class Ticket:
    """Incidencia reportada. Guarda la prioridad sugerida por la IA y la vigente.

    Raises:
        ValueError: al crearlo, si el estado o una prioridad no son válidos.
    """

    ticket_id: int
    estado: str
    prioridad_sugerida: str | None  # resultado de la IA; None si el análisis está pendiente
    prioridad_actual: str | None  # valor vigente

    def __post_init__(self) -> None:
        """Rechaza estados y prioridades fuera de las listas.

        Así un estado como "Cerrado" o " cerrado" no pasa como si fuera un ticket abierto.

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
    """Registro inmutable de un cambio de prioridad (entidad HistorialPrioridad del diseño)."""

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
    """La prioridad pedida no está en PRIORIDADES."""

    codigo_http = 400


class JustificacionRequeridaError(ErrorDePrioridad):
    """Falta la justificación y la regla de HU-03 la exige."""

    codigo_http = 400


class JustificacionInvalidaError(ErrorDePrioridad):
    """La justificación no es texto, es demasiado larga o tiene caracteres de control."""

    codigo_http = 400


class PermisoDenegadoError(ErrorDePrioridad):
    """El usuario no tiene el rol que pide la operación."""

    codigo_http = 403


class TicketNoEncontradoError(ErrorDePrioridad):
    """No existe un ticket con ese id."""

    codigo_http = 404


class ConflictoError(ErrorDePrioridad):
    """El ticket está cerrado o ya tiene la prioridad pedida."""

    codigo_http = 409

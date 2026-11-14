"""HU-03: ajuste manual de prioridad por el técnico de soporte."""
from datetime import datetime, timezone

from .modelos import (
    ConflictoError,
    ESTADO_CERRADO,
    JustificacionInvalidaError,
    JustificacionRequeridaError,
    LONGITUD_MAXIMA_JUSTIFICACION,
    PermisoDenegadoError,
    PrioridadInvalidaError,
    PRIORIDADES,
    RegistroAuditoria,
    ROL_SOPORTE,
    Ticket,
    TicketNoEncontradoError,
    Usuario,
)


def _exige_justificacion(ticket: Ticket, nueva_prioridad: str) -> bool:
    """Regla de HU-03: hay que justificar cuando el técnico se aparta de la sugerencia de la IA.

    Si el análisis está pendiente, `prioridad_sugerida` es None y siempre se exige.
    """
    return nueva_prioridad != ticket.prioridad_sugerida


def _normalizar_justificacion(justificacion: object) -> str | None:
    """Limpia la justificación; devuelve None si está ausente o es solo espacios."""
    if justificacion is None:
        return None
    if not isinstance(justificacion, str):
        raise JustificacionInvalidaError("La justificación debe ser texto")
    limpia = justificacion.strip()
    if len(limpia) > LONGITUD_MAXIMA_JUSTIFICACION:
        raise JustificacionInvalidaError(
            f"La justificación supera {LONGITUD_MAXIMA_JUSTIFICACION} caracteres"
        )
    if any(not caracter.isprintable() for caracter in limpia):
        raise JustificacionInvalidaError(
            "La justificación no puede tener saltos de línea ni caracteres de control"
        )
    return limpia or None


def _validar_peticion(usuario: Usuario, nueva_prioridad: str) -> None:
    """Validaciones que no necesitan consultar el ticket."""
    if usuario.rol != ROL_SOPORTE:
        raise PermisoDenegadoError("Solo el técnico de soporte puede cambiar la prioridad")
    if nueva_prioridad not in PRIORIDADES:
        raise PrioridadInvalidaError(f"Prioridad inválida: {nueva_prioridad!r}")


def _validar_ticket(ticket: Ticket | None, ticket_id: int, nueva_prioridad: str) -> Ticket:
    """Validaciones sobre el estado del ticket. Devuelve el ticket ya comprobado."""
    if ticket is None:
        raise TicketNoEncontradoError(f"No existe el ticket {ticket_id}")
    if ticket.estado == ESTADO_CERRADO:
        raise ConflictoError("El ticket está cerrado")
    if nueva_prioridad == ticket.prioridad_actual:
        raise ConflictoError("El ticket ya tiene esa prioridad")
    return ticket


def cambiar_prioridad(
    repositorio,
    ticket_id: int,
    nueva_prioridad: str,
    usuario: Usuario,
    justificacion: str | None = None,
    *,
    ahora: datetime | None = None,
) -> RegistroAuditoria:
    """Cambia la prioridad vigente de un ticket y deja registro de auditoría."""
    if ahora is not None and ahora.utcoffset() is None:
        raise ValueError("`ahora` debe tener zona horaria (por ejemplo, timezone.utc)")
    _validar_peticion(usuario, nueva_prioridad)
    ticket = _validar_ticket(repositorio.obtener_ticket(ticket_id), ticket_id, nueva_prioridad)

    justificacion_limpia = _normalizar_justificacion(justificacion)
    if _exige_justificacion(ticket, nueva_prioridad) and not justificacion_limpia:
        raise JustificacionRequeridaError(
            "Se necesita justificación para apartarse de la sugerencia de la IA"
        )

    registro = RegistroAuditoria(
        ticket_id=ticket_id,
        usuario_id=usuario.usuario_id,
        prioridad_anterior=ticket.prioridad_actual,
        prioridad_sugerida=ticket.prioridad_sugerida,
        prioridad_final=nueva_prioridad,
        justificacion=justificacion_limpia,
        fecha_cambio=ahora or datetime.now(timezone.utc),
    )
    repositorio.guardar_cambio_prioridad(ticket_id, nueva_prioridad, registro)
    return registro

"""HU-03: ajuste manual de prioridad por el técnico de soporte."""
from datetime import datetime, timezone

from .modelos import (
    ConflictoError,
    ESTADO_CERRADO,
    JustificacionRequeridaError,
    PermisoDenegadoError,
    PrioridadInvalidaError,
    PRIORIDADES,
    RegistroAuditoria,
    ROL_SOPORTE,
    TicketNoEncontradoError,
    Usuario,
)


def cambiar_prioridad(
    repositorio,
    ticket_id: int,
    nueva_prioridad: str,
    usuario: Usuario,
    justificacion: str | None = None,
    ahora: datetime | None = None,
) -> RegistroAuditoria:
    """Cambia la prioridad vigente de un ticket y deja registro de auditoría."""
    if usuario.rol != ROL_SOPORTE:
        raise PermisoDenegadoError("Solo el técnico de soporte puede cambiar la prioridad")

    if nueva_prioridad not in PRIORIDADES:
        raise PrioridadInvalidaError(f"Prioridad inválida: {nueva_prioridad!r}")

    ticket = repositorio.obtener_ticket(ticket_id)
    if ticket is None:
        raise TicketNoEncontradoError(f"No existe el ticket {ticket_id}")

    if ticket.estado == ESTADO_CERRADO:
        raise ConflictoError("El ticket está cerrado")

    if nueva_prioridad == ticket.prioridad_actual:
        raise ConflictoError("El ticket ya tiene esa prioridad")

    justificacion_limpia = (justificacion or "").strip()
    if nueva_prioridad != ticket.prioridad_sugerida and not justificacion_limpia:
        raise JustificacionRequeridaError("Se necesita justificación para apartarse de la sugerencia de la IA")

    registro = RegistroAuditoria(
        ticket_id=ticket_id,
        usuario_id=usuario.usuario_id,
        prioridad_anterior=ticket.prioridad_actual,
        prioridad_sugerida=ticket.prioridad_sugerida,
        prioridad_final=nueva_prioridad,
        justificacion=justificacion_limpia or None,
        fecha_cambio=ahora or datetime.now(timezone.utc),
    )
    repositorio.guardar_cambio_prioridad(ticket_id, nueva_prioridad, registro)
    return registro

"""HU-03: ajuste manual de prioridad por el técnico de soporte."""
from datetime import datetime

from .modelos import RegistroAuditoria, Usuario


def cambiar_prioridad(
    repositorio,
    ticket_id: int,
    nueva_prioridad: str,
    usuario: Usuario,
    justificacion: str | None = None,
    ahora: datetime | None = None,
) -> RegistroAuditoria:
    """Contrato en el README. Aún sin implementar (fase roja)."""
    raise NotImplementedError

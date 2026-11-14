"""Repositorio en memoria: reemplaza a la base de datos operativa y a la de auditoría."""
from dataclasses import replace

from .modelos import RegistroAuditoria, Ticket


class RepositorioEnMemoria:
    """Guarda tickets y registros de auditoría en memoria.

    Guarda y entrega copias de los tickets, así que nadie puede cambiar la prioridad
    modificando el objeto que recibió: el único camino es guardar_cambio_prioridad,
    que siempre deja auditoría.
    """

    def __init__(self, tickets: list[Ticket] | tuple[Ticket, ...] = ()):
        """Recibe los tickets iniciales; guarda una copia de cada uno."""
        self._tickets = {t.ticket_id: replace(t) for t in tickets}
        self.auditoria: list[RegistroAuditoria] = []

    def obtener_ticket(self, ticket_id: int) -> Ticket | None:
        """Devuelve una copia del ticket con ese id, o None si no existe."""
        ticket = self._tickets.get(ticket_id)
        return replace(ticket) if ticket is not None else None

    def guardar_cambio_prioridad(
        self, ticket_id: int, prioridad_final: str, registro: RegistroAuditoria
    ) -> None:
        """Actualiza la prioridad vigente y guarda el registro de auditoría juntos.

        Raises:
            KeyError: si el ticket no existe. cambiar_prioridad lo comprueba antes.
        """
        self._tickets[ticket_id].prioridad_actual = prioridad_final
        self.auditoria.append(registro)

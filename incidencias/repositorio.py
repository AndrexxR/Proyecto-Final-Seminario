"""Repositorio en memoria: sustituye a la base de datos operativa y a la de auditoría."""
from .modelos import RegistroAuditoria, Ticket


class RepositorioEnMemoria:
    def __init__(self, tickets: list[Ticket] | tuple[Ticket, ...] = ()):
        self._tickets = {t.ticket_id: t for t in tickets}
        self.auditoria: list[RegistroAuditoria] = []

    def obtener_ticket(self, ticket_id: int) -> Ticket | None:
        return self._tickets.get(ticket_id)

    def guardar_cambio_prioridad(
        self, ticket_id: int, prioridad_final: str, registro: RegistroAuditoria
    ) -> None:
        """Actualiza la prioridad vigente y guarda el registro de auditoría juntos."""
        self._tickets[ticket_id].prioridad_actual = prioridad_final
        self.auditoria.append(registro)

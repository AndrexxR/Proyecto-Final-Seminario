"""Pruebas nuevas de la semana 6: una por hallazgo corregido y pruebas de abuso."""
import unittest

from incidencias.modelos import Ticket
from incidencias.repositorio import RepositorioEnMemoria


class EstadoDelTicket(unittest.TestCase):
    """H-01: el estado debe estar en la lista (evita saltarse el bloqueo de cerrado)."""

    def test_estado_con_otra_capitalizacion_o_espacios_se_rechaza(self):
        for estado in ("Cerrado", " cerrado", "CERRADO", "", "borrado"):
            with self.subTest(estado=estado):
                with self.assertRaises(ValueError):
                    Ticket(ticket_id=1, estado=estado, prioridad_sugerida="Media",
                           prioridad_actual="Media")

    def test_prioridad_guardada_fuera_de_la_lista_se_rechaza(self):
        with self.assertRaises(ValueError):
            Ticket(ticket_id=1, estado="abierto", prioridad_sugerida="Urgente",
                   prioridad_actual="Media")


class CopiasDelRepositorio(unittest.TestCase):
    """H-02 (abuso): cambiar el objeto recibido no debe saltarse la auditoría."""

    def test_modificar_el_ticket_obtenido_no_cambia_el_repositorio(self):
        repo = RepositorioEnMemoria([Ticket(1, "abierto", "Media", "Media")])
        ticket = repo.obtener_ticket(1)
        ticket.prioridad_actual = "Baja"
        self.assertEqual(repo.obtener_ticket(1).prioridad_actual, "Media")
        self.assertEqual(repo.auditoria, [])

    def test_modificar_el_ticket_original_no_cambia_el_repositorio(self):
        original = Ticket(1, "abierto", "Media", "Media")
        repo = RepositorioEnMemoria([original])
        original.estado = "cerrado"
        self.assertEqual(repo.obtener_ticket(1).estado, "abierto")


if __name__ == "__main__":
    unittest.main()

"""Pruebas nuevas de la semana 6: una por hallazgo corregido y pruebas de abuso."""
import unittest

from incidencias.modelos import Ticket


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


if __name__ == "__main__":
    unittest.main()

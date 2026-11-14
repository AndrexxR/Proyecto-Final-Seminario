"""Pruebas de HU-03 (ajuste manual de prioridad). Se escribieron ANTES de la implementación."""
import unittest
from datetime import datetime, timezone

from incidencias.modelos import (
    ConflictoError,
    JustificacionRequeridaError,
    PermisoDenegadoError,
    PrioridadInvalidaError,
    Ticket,
    TicketNoEncontradoError,
    Usuario,
)
from incidencias.prioridad import cambiar_prioridad
from incidencias.repositorio import RepositorioEnMemoria

TECNICO = Usuario(usuario_id=7, rol="soporte")
OPERATIVO = Usuario(usuario_id=3, rol="operativo")
AHORA = datetime(2026, 11, 10, 9, 30, tzinfo=timezone.utc)
MOTIVO = "Afecta el cierre de caja"


def crear_repo(estado="abierto", sugerida="Media", actual="Media"):
    ticket = Ticket(ticket_id=1, estado=estado, prioridad_sugerida=sugerida, prioridad_actual=actual)
    return RepositorioEnMemoria([ticket])


class CasosNormales(unittest.TestCase):
    def test_corregir_prioridad_con_justificacion_actualiza_la_prioridad_actual(self):
        repo = crear_repo(sugerida="Media", actual="Media")
        cambiar_prioridad(repo, 1, "Alta", TECNICO, MOTIVO, ahora=AHORA)
        self.assertEqual(repo.obtener_ticket(1).prioridad_actual, "Alta")

    def test_corregir_prioridad_conserva_la_sugerencia_original_de_la_ia(self):
        repo = crear_repo(sugerida="Media", actual="Media")
        cambiar_prioridad(repo, 1, "Alta", TECNICO, MOTIVO, ahora=AHORA)
        self.assertEqual(repo.obtener_ticket(1).prioridad_sugerida, "Media")

    def test_corregir_prioridad_registra_auditoria_completa(self):
        repo = crear_repo(sugerida="Media", actual="Media")
        registro = cambiar_prioridad(repo, 1, "Alta", TECNICO, MOTIVO, ahora=AHORA)
        self.assertEqual(repo.auditoria, [registro])
        self.assertEqual(registro.ticket_id, 1)
        self.assertEqual(registro.usuario_id, 7)
        self.assertEqual(registro.prioridad_anterior, "Media")
        self.assertEqual(registro.prioridad_sugerida, "Media")
        self.assertEqual(registro.prioridad_final, "Alta")
        self.assertEqual(registro.justificacion, MOTIVO)
        self.assertEqual(registro.fecha_cambio, AHORA)

    def test_volver_a_la_sugerencia_de_la_ia_no_exige_justificacion(self):
        # Un cambio previo dejó la prioridad en Baja; el técnico retoma lo que sugirió la IA.
        repo = crear_repo(sugerida="Media", actual="Baja")
        registro = cambiar_prioridad(repo, 1, "Media", TECNICO, ahora=AHORA)
        self.assertEqual(repo.obtener_ticket(1).prioridad_actual, "Media")
        self.assertIsNone(registro.justificacion)


class CasosLimite(unittest.TestCase):
    def test_justificacion_de_solo_espacios_cuenta_como_ausente(self):
        repo = crear_repo()
        with self.assertRaises(JustificacionRequeridaError):
            cambiar_prioridad(repo, 1, "Alta", TECNICO, "   ", ahora=AHORA)

    def test_ticket_pendiente_de_clasificacion_exige_justificacion(self):
        repo = crear_repo(estado="pendiente_clasificacion", sugerida=None, actual=None)
        with self.assertRaises(JustificacionRequeridaError):
            cambiar_prioridad(repo, 1, "Alta", TECNICO, ahora=AHORA)

    def test_ticket_pendiente_de_clasificacion_acepta_prioridad_con_justificacion(self):
        repo = crear_repo(estado="pendiente_clasificacion", sugerida=None, actual=None)
        registro = cambiar_prioridad(repo, 1, "Alta", TECNICO, MOTIVO, ahora=AHORA)
        self.assertIsNone(registro.prioridad_anterior)
        self.assertIsNone(registro.prioridad_sugerida)
        self.assertEqual(repo.obtener_ticket(1).prioridad_actual, "Alta")

    def test_justificacion_se_guarda_sin_espacios_sobrantes(self):
        repo = crear_repo()
        registro = cambiar_prioridad(repo, 1, "Alta", TECNICO, f"  {MOTIVO}  ", ahora=AHORA)
        self.assertEqual(registro.justificacion, MOTIVO)

    def test_se_aceptan_la_primera_y_la_ultima_prioridad_de_la_lista(self):
        for nueva in ("Baja", "Alta"):
            with self.subTest(prioridad=nueva):
                repo = crear_repo(sugerida="Media", actual="Media")
                cambiar_prioridad(repo, 1, nueva, TECNICO, MOTIVO, ahora=AHORA)
                self.assertEqual(repo.obtener_ticket(1).prioridad_actual, nueva)

    def test_repetir_la_prioridad_vigente_es_conflicto(self):
        repo = crear_repo(sugerida="Media", actual="Alta")
        with self.assertRaises(ConflictoError):
            cambiar_prioridad(repo, 1, "Alta", TECNICO, MOTIVO, ahora=AHORA)


class CasosDeError(unittest.TestCase):
    def test_prioridad_invalida_se_rechaza_sin_cambiar_nada(self):
        repo = crear_repo(sugerida="Media", actual="Media")
        for invalida in ("Urgente", "alta", "", None):
            with self.subTest(prioridad=invalida):
                with self.assertRaises(PrioridadInvalidaError):
                    cambiar_prioridad(repo, 1, invalida, TECNICO, MOTIVO, ahora=AHORA)
        self.assertEqual(repo.obtener_ticket(1).prioridad_actual, "Media")
        self.assertEqual(repo.auditoria, [])

    def test_ticket_inexistente_lanza_error_404(self):
        repo = crear_repo()
        with self.assertRaises(TicketNoEncontradoError) as contexto:
            cambiar_prioridad(repo, 999, "Alta", TECNICO, MOTIVO, ahora=AHORA)
        self.assertEqual(contexto.exception.codigo_http, 404)

    def test_ticket_cerrado_no_permite_cambiar_la_prioridad(self):
        repo = crear_repo(estado="cerrado")
        with self.assertRaises(ConflictoError):
            cambiar_prioridad(repo, 1, "Alta", TECNICO, MOTIVO, ahora=AHORA)
        self.assertEqual(repo.auditoria, [])

    def test_usuario_que_no_es_tecnico_no_puede_cambiar_la_prioridad(self):
        repo = crear_repo()
        with self.assertRaises(PermisoDenegadoError):
            cambiar_prioridad(repo, 1, "Alta", OPERATIVO, MOTIVO, ahora=AHORA)
        self.assertEqual(repo.obtener_ticket(1).prioridad_actual, "Media")


if __name__ == "__main__":
    unittest.main()

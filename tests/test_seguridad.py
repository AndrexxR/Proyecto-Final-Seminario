"""Pruebas nuevas de la semana 6: una por hallazgo corregido y pruebas de abuso."""
import unittest
from datetime import datetime, timezone

from incidencias.modelos import (
    LONGITUD_MAXIMA_JUSTIFICACION,
    JustificacionInvalidaError,
    PermisoDenegadoError,
    Ticket,
    Usuario,
)
from incidencias.prioridad import cambiar_prioridad
from incidencias.repositorio import RepositorioEnMemoria

TECNICO = Usuario(usuario_id=7, rol="soporte")
AHORA = datetime(2026, 11, 14, 9, 0, tzinfo=timezone.utc)


def crear_repo():
    return RepositorioEnMemoria([Ticket(1, "abierto", "Media", "Media")])


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


class ValidacionDeLaJustificacion(unittest.TestCase):
    """H-03 a H-05: la justificación se valida antes de guardar nada."""

    def assert_rechazada_sin_cambios(self, justificacion):
        repo = crear_repo()
        with self.assertRaises(JustificacionInvalidaError) as contexto:
            cambiar_prioridad(repo, 1, "Alta", TECNICO, justificacion, ahora=AHORA)
        self.assertEqual(contexto.exception.codigo_http, 400)
        self.assertEqual(repo.obtener_ticket(1).prioridad_actual, "Media")
        self.assertEqual(repo.auditoria, [])

    def test_justificacion_que_no_es_texto_da_error_400(self):
        for valor in (12345, ["Afecta caja"], {"motivo": "x"}):
            with self.subTest(valor=valor):
                self.assert_rechazada_sin_cambios(valor)

    def test_justificacion_mas_larga_que_el_limite_se_rechaza(self):
        self.assert_rechazada_sin_cambios("x" * (LONGITUD_MAXIMA_JUSTIFICACION + 1))

    def test_justificacion_justo_en_el_limite_se_acepta(self):
        repo = crear_repo()
        texto = "x" * LONGITUD_MAXIMA_JUSTIFICACION
        registro = cambiar_prioridad(repo, 1, "Alta", TECNICO, texto, ahora=AHORA)
        self.assertEqual(registro.justificacion, texto)

    def test_justificacion_con_saltos_de_linea_o_control_se_rechaza(self):
        for texto in ("ok\n2026-01-01 ADMIN borró auditoría", "a\rb", "a\x00b", "a\x1b[2Jb"):
            with self.subTest(texto=texto):
                self.assert_rechazada_sin_cambios(texto)

    def test_justificacion_con_tildes_y_signos_se_acepta(self):
        repo = crear_repo()
        texto = "Afecta el cierre de caja: ¿urgente? Sí, 100 %"
        registro = cambiar_prioridad(repo, 1, "Alta", TECNICO, texto, ahora=AHORA)
        self.assertEqual(registro.justificacion, texto)


class FechaDeLaAuditoria(unittest.TestCase):
    """H-06: la fecha de la auditoría no se puede pasar por posición ni sin zona horaria."""

    def test_ahora_no_se_acepta_por_posicion(self):
        with self.assertRaises(TypeError):
            cambiar_prioridad(crear_repo(), 1, "Alta", TECNICO, "Motivo", AHORA)

    def test_ahora_sin_zona_horaria_se_rechaza_sin_cambios(self):
        repo = crear_repo()
        with self.assertRaises(ValueError):
            cambiar_prioridad(repo, 1, "Alta", TECNICO, "Motivo", ahora=datetime(1999, 1, 1))
        self.assertEqual(repo.auditoria, [])

    def test_sin_ahora_se_usa_la_hora_actual_en_utc(self):
        antes = datetime.now(timezone.utc)
        registro = cambiar_prioridad(crear_repo(), 1, "Alta", TECNICO, "Motivo")
        self.assertLessEqual(antes, registro.fecha_cambio)
        self.assertEqual(registro.fecha_cambio.utcoffset().total_seconds(), 0)


class AbusoDeControlDeAcceso(unittest.TestCase):
    """H-08: ningún rol distinto de "soporte" exacto puede cambiar la prioridad."""

    def test_roles_sin_permiso_o_parecidos_a_soporte_reciben_403_sin_cambios(self):
        for rol in ("líder", "operativo", "Soporte", " soporte", "soporte ", "SOPORTE", "", None):
            with self.subTest(rol=rol):
                repo = crear_repo()
                with self.assertRaises(PermisoDenegadoError) as contexto:
                    cambiar_prioridad(repo, 1, "Alta", Usuario(9, rol), "Motivo", ahora=AHORA)
                self.assertEqual(contexto.exception.codigo_http, 403)
                self.assertEqual(repo.obtener_ticket(1).prioridad_actual, "Media")
                self.assertEqual(repo.auditoria, [])

    def test_permiso_se_revisa_antes_que_la_existencia_del_ticket(self):
        # Un usuario sin permiso no debe poder averiguar qué tickets existen (403, no 404).
        with self.assertRaises(PermisoDenegadoError):
            cambiar_prioridad(crear_repo(), 999, "Alta", Usuario(9, "operativo"), "x", ahora=AHORA)


if __name__ == "__main__":
    unittest.main()

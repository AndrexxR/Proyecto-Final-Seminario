"""Reglas de HU-03 con los datos sintéticos de tests/datos/ (fixtures en conftest.py)."""
from datetime import datetime, timezone

import pytest

from incidencias.modelos import (
    ConflictoError,
    JustificacionInvalidaError,
    JustificacionRequeridaError,
    PermisoDenegadoError,
)
from incidencias.prioridad import cambiar_prioridad

AHORA = datetime(2026, 11, 21, 10, 0, tzinfo=timezone.utc)
ABIERTO = 101  # Panadería La Ñapa: sugerida Media, vigente Media
PENDIENTE = 102  # Droguería: sin sugerencia de la IA
CERRADO = 104  # Tienda Doña Inés


def test_los_datos_traen_los_casos_dificiles(datos):
    # Si alguien recorta el archivo de datos, esta prueba avisa antes que las demás.
    nombres = " ".join(u["nombre"] for u in datos["usuarios"])
    for caso in ("ñ", "á", "'"):
        assert caso in nombres
    assert "" in [u["nombre"] for u in datos["usuarios"]]
    assert 0 in [t["existencias_afectadas"] for t in datos["tickets"]]
    assert "" in [t["descripcion"] for t in datos["tickets"]]


def test_ningun_usuario_sin_rol_soporte_exacto_puede_cambiar(usuarios, repo_sintetico):
    assert len(usuarios["sin_permiso"]) == 5  # operativo x2, líder, "Soporte" y rol vacío
    for usuario in usuarios["sin_permiso"]:
        with pytest.raises(PermisoDenegadoError):
            cambiar_prioridad(repo_sintetico, ABIERTO, "Alta", usuario, "Motivo", ahora=AHORA)
    assert repo_sintetico.obtener_ticket(ABIERTO).prioridad_actual == "Media"
    assert repo_sintetico.auditoria == []


def test_cada_tecnico_puede_cambiar_la_prioridad(usuarios, repo_sintetico):
    assert [u.usuario_id for u in usuarios["tecnicos"]] == [7, 8]
    for usuario, nueva in zip(usuarios["tecnicos"], ("Alta", "Baja"), strict=True):
        registro = cambiar_prioridad(
            repo_sintetico, ABIERTO, nueva, usuario, "Afecta caja", ahora=AHORA
        )
        assert (registro.usuario_id, registro.prioridad_final) == (usuario.usuario_id, nueva)
    assert repo_sintetico.obtener_ticket(ABIERTO).prioridad_actual == "Baja"
    assert len(repo_sintetico.auditoria) == 2


def test_justificaciones_validas_se_guardan_limpias(datos, usuarios, repo_sintetico):
    tecnico = usuarios["tecnicos"][0]
    validas = datos["justificaciones_validas"]
    # Alterna Alta y Baja para no pedir nunca la prioridad vigente (eso sería 409).
    prioridades = ["Alta" if i % 2 == 0 else "Baja" for i in range(len(validas))]
    for caso, nueva in zip(validas, prioridades, strict=True):
        registro = cambiar_prioridad(
            repo_sintetico, ABIERTO, nueva, tecnico, caso["texto"], ahora=AHORA
        )
        assert registro.justificacion == caso["guardada"]


def test_justificaciones_ausentes_no_sirven_si_no_hay_sugerencia(datos, usuarios, repo_sintetico):
    tecnico = usuarios["tecnicos"][0]
    for texto in datos["justificaciones_ausentes"]:
        with pytest.raises(JustificacionRequeridaError):
            cambiar_prioridad(repo_sintetico, PENDIENTE, "Alta", tecnico, texto, ahora=AHORA)
    assert repo_sintetico.auditoria == []


def test_justificaciones_invalidas_se_rechazan(datos, usuarios, repo_sintetico):
    tecnico = usuarios["tecnicos"][0]
    for texto in datos["justificaciones_invalidas"]:
        with pytest.raises(JustificacionInvalidaError):
            cambiar_prioridad(repo_sintetico, ABIERTO, "Alta", tecnico, texto, ahora=AHORA)
    assert repo_sintetico.auditoria == []


def test_ticket_cerrado_de_los_datos_no_admite_cambios(usuarios, repo_sintetico):
    with pytest.raises(ConflictoError):
        cambiar_prioridad(
            repo_sintetico, CERRADO, "Alta", usuarios["tecnicos"][0], "Motivo", ahora=AHORA
        )

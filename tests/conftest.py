"""Fixtures compartidos: datos sintéticos de usuarios, tickets y justificaciones."""
import json
from pathlib import Path

import pytest

from incidencias.modelos import Ticket, Usuario
from incidencias.repositorio import RepositorioEnMemoria

RUTA_DATOS = Path(__file__).parent / "datos" / "datos_sinteticos.json"


@pytest.fixture(scope="session")
def datos():
    """Contenido de tests/datos/datos_sinteticos.json (solo lectura)."""
    with RUTA_DATOS.open(encoding="utf-8") as archivo:
        return json.load(archivo)


@pytest.fixture
def usuarios(datos):
    """Usuarios sintéticos como objetos Usuario, agrupados por si tienen rol "soporte" exacto."""
    todos = [Usuario(u["usuario_id"], u["rol"]) for u in datos["usuarios"]]
    return {
        "tecnicos": [u for u in todos if u.rol == "soporte"],
        "sin_permiso": [u for u in todos if u.rol != "soporte"],
    }


@pytest.fixture
def repo_sintetico(datos):
    """Repositorio en memoria cargado con los tickets sintéticos."""
    tickets = [
        Ticket(t["ticket_id"], t["estado"], t["prioridad_sugerida"], t["prioridad_actual"])
        for t in datos["tickets"]
    ]
    return RepositorioEnMemoria(tickets)

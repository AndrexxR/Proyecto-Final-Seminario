"""HU-03: ajuste manual de prioridad por el técnico de soporte."""
import unicodedata
from datetime import datetime, timezone

from .modelos import (
    ConflictoError,
    ESTADO_CERRADO,
    JustificacionInvalidaError,
    JustificacionRequeridaError,
    LONGITUD_MAXIMA_JUSTIFICACION,
    PermisoDenegadoError,
    PrioridadInvalidaError,
    PRIORIDADES,
    RegistroAuditoria,
    ROL_SOPORTE,
    Ticket,
    TicketNoEncontradoError,
    Usuario,
)

# Categorías Unicode que no se admiten en la justificación: caracteres de control (Cc,
# incluye \n, \r y \t) y separadores de línea y de párrafo (Zl, Zp). Un espacio no
# separable es un espacio (Zs) y sí se admite.
_CATEGORIAS_PROHIBIDAS = ("Cc", "Zl", "Zp")


def _exige_justificacion(ticket: Ticket, nueva_prioridad: str) -> bool:
    """Regla de HU-03: hay que justificar cuando el técnico se aparta de la sugerencia de la IA.

    Si el análisis está pendiente, `prioridad_sugerida` es None y siempre se exige.
    """
    return nueva_prioridad != ticket.prioridad_sugerida


def _normalizar_justificacion(justificacion: object) -> str | None:
    """Limpia y valida la justificación que escribió el técnico.

    Args:
        justificacion: texto recibido en la petición; puede ser None.

    Returns:
        El texto sin espacios al inicio ni al final, o None si venía None, vacío o
        con solo espacios.

    Raises:
        JustificacionInvalidaError: (400) si no es texto, si supera
            LONGITUD_MAXIMA_JUSTIFICACION caracteres o si tiene saltos de línea u
            otros caracteres de control.
    """
    if justificacion is None:
        return None
    if not isinstance(justificacion, str):
        raise JustificacionInvalidaError("La justificación debe ser texto")
    limpia = justificacion.strip()
    if len(limpia) > LONGITUD_MAXIMA_JUSTIFICACION:
        raise JustificacionInvalidaError(
            f"La justificación supera {LONGITUD_MAXIMA_JUSTIFICACION} caracteres"
        )
    if any(unicodedata.category(caracter) in _CATEGORIAS_PROHIBIDAS for caracter in limpia):
        raise JustificacionInvalidaError(
            "La justificación no puede tener saltos de línea ni caracteres de control"
        )
    return limpia or None


def _validar_peticion(usuario: Usuario, nueva_prioridad: str) -> None:
    """Valida el rol del usuario y la prioridad pedida, sin consultar el ticket.

    El rol se revisa primero para que un usuario sin permiso no pueda averiguar
    nada del sistema (recibe 403 aunque el resto de la petición esté mal).

    Raises:
        PermisoDenegadoError: (403) si el rol no es exactamente ROL_SOPORTE.
        PrioridadInvalidaError: (400) si la prioridad no está en PRIORIDADES.
    """
    if usuario.rol != ROL_SOPORTE:
        raise PermisoDenegadoError("Solo el técnico de soporte puede cambiar la prioridad")
    if nueva_prioridad not in PRIORIDADES:
        raise PrioridadInvalidaError(f"Prioridad inválida: {nueva_prioridad!r}")


def _validar_ticket(ticket: Ticket | None, ticket_id: int, nueva_prioridad: str) -> Ticket:
    """Valida que el ticket exista, esté abierto y no tenga ya esa prioridad.

    Args:
        ticket: el ticket que devolvió el repositorio, o None si no existe.
        ticket_id: id pedido, solo para el mensaje de error.
        nueva_prioridad: prioridad que se quiere poner.

    Returns:
        El mismo ticket, ya comprobado.

    Raises:
        TicketNoEncontradoError: (404) si `ticket` es None.
        ConflictoError: (409) si el ticket está cerrado o ya tiene `nueva_prioridad`.
    """
    if ticket is None:
        raise TicketNoEncontradoError(f"No existe el ticket {ticket_id}")
    if ticket.estado == ESTADO_CERRADO:
        raise ConflictoError("El ticket está cerrado")
    if nueva_prioridad == ticket.prioridad_actual:
        raise ConflictoError("El ticket ya tiene esa prioridad")
    return ticket


def cambiar_prioridad(
    repositorio,
    ticket_id: int,
    nueva_prioridad: str,
    usuario: Usuario,
    justificacion: str | None = None,
    *,
    ahora: datetime | None = None,
) -> RegistroAuditoria:
    """Cambia la prioridad vigente de un ticket y deja registro de auditoría (HU-03).

    Hace todas las validaciones antes de guardar, así que un error nunca deja
    cambios parciales. Nunca modifica `prioridad_sugerida`.

    Args:
        repositorio: objeto con `obtener_ticket(ticket_id)` y
            `guardar_cambio_prioridad(ticket_id, prioridad, registro)`, por ejemplo
            RepositorioEnMemoria.
        ticket_id: id del ticket que se cambia.
        nueva_prioridad: "Baja", "Media" o "Alta" (distingue mayúsculas).
        usuario: quien hace el cambio; debe tener rol "soporte".
        justificacion: obligatoria si `nueva_prioridad` es distinta de la sugerida por
            la IA o si aún no hay sugerencia. Se guarda sin espacios en los extremos.
        ahora: solo por nombre y con zona horaria; existe para las pruebas. Si es
            None se usa la hora actual en UTC. La API no debe tomarlo de la petición.

    Returns:
        El RegistroAuditoria creado y guardado.

    Raises:
        ValueError: si `ahora` no tiene zona horaria.
        PermisoDenegadoError: (403) si el usuario no es técnico de soporte.
        PrioridadInvalidaError: (400) si la prioridad no está en la lista.
        TicketNoEncontradoError: (404) si el ticket no existe.
        ConflictoError: (409) si el ticket está cerrado o ya tiene esa prioridad.
        JustificacionInvalidaError: (400) si la justificación no es texto, es
            demasiado larga o tiene caracteres de control.
        JustificacionRequeridaError: (400) si falta la justificación exigida.
    """
    if ahora is not None and ahora.utcoffset() is None:
        raise ValueError("`ahora` debe tener zona horaria (por ejemplo, timezone.utc)")
    _validar_peticion(usuario, nueva_prioridad)
    ticket = _validar_ticket(repositorio.obtener_ticket(ticket_id), ticket_id, nueva_prioridad)

    justificacion_limpia = _normalizar_justificacion(justificacion)
    if _exige_justificacion(ticket, nueva_prioridad) and not justificacion_limpia:
        raise JustificacionRequeridaError(
            "Se necesita justificación para apartarse de la sugerencia de la IA"
        )

    registro = RegistroAuditoria(
        ticket_id=ticket_id,
        usuario_id=usuario.usuario_id,
        prioridad_anterior=ticket.prioridad_actual,
        prioridad_sugerida=ticket.prioridad_sugerida,
        prioridad_final=nueva_prioridad,
        justificacion=justificacion_limpia,
        fecha_cambio=ahora or datetime.now(timezone.utc),
    )
    repositorio.guardar_cambio_prioridad(ticket_id, nueva_prioridad, registro)
    return registro

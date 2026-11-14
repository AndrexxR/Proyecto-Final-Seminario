"""Demostración de HU-03 por consola: python -m incidencias."""
from .modelos import ErrorDePrioridad, Ticket, Usuario
from .prioridad import cambiar_prioridad
from .repositorio import RepositorioEnMemoria


def main() -> None:
    """Ejecuta los ejemplos del contrato de HU-03 e imprime el resultado de cada uno."""
    tecnico = Usuario(usuario_id=7, rol="soporte")
    operativo = Usuario(usuario_id=3, rol="operativo")
    repo = RepositorioEnMemoria([Ticket(1, "abierto", "Media", "Media")])

    intentos = [
        ("Técnico sube a Alta con justificación", 1, "Alta", tecnico, "Afecta el cierre de caja"),
        ("Operativo intenta cambiarla", 1, "Baja", operativo, "Quiero"),
        ("Técnico pide una prioridad que no existe", 1, "Urgente", tecnico, "x"),
        ("Técnico cambia un ticket que no existe", 999, "Alta", tecnico, "x"),
        ("Técnico vuelve a la sugerencia de la IA", 1, "Media", tecnico, None),
    ]
    for descripcion, ticket_id, prioridad, usuario, justificacion in intentos:
        try:
            registro = cambiar_prioridad(repo, ticket_id, prioridad, usuario, justificacion)
            print(f"OK    {descripcion}: {registro.prioridad_anterior} -> "
                  f"{registro.prioridad_final} (justificación: {registro.justificacion!r})")
        except ErrorDePrioridad as error:
            print(f"{error.codigo_http}   {descripcion}: {error}")

    print(f"\nRegistros de auditoría guardados: {len(repo.auditoria)}")


if __name__ == "__main__":
    main()

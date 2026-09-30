"""User-facing texts, kept in one place (Spanish, like the rest of TripTrace)."""

HELP = (
    "Hola, soy el bot de TripTrace. Desde acá vas a poder consultar tus viajes "
    "y estadísticas.\n\n"
    "Comandos:\n"
    "/ayuda: muestra esta ayuda\n"
    "/estado: verifica la conexión con TripTrace"
)

STATUS_OK = "✅ Conectado a TripTrace como {username}."
API_UNAVAILABLE = "⚠️ TripTrace no está disponible en este momento. Probá de nuevo en un rato."
API_ERROR = "⚠️ TripTrace respondió con un error ({status_code}). Revisá los logs del bot."
UNEXPECTED_ERROR = "⚠️ Algo salió mal. Revisá los logs del bot."

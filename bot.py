"""Telegram bot for TripTrace — a lightweight alternative client to the
Android app, using Telegram's own Live Location feature for GPS tracking
instead of a native foreground service.

NOTE: sending data to trip-trace-api is commented out for now — this build
just accumulates whatever the bot receives from Telegram (one-off and live
location updates) in memory, and prints them out on /finalizar, so we can
confirm that part works end to end before wiring the API calls back up.
Search for "trip-trace-api calls" below.
"""

import logging
import os
from datetime import datetime, timezone
from typing import Optional

# import httpx  # not used while the API calls below are commented out
from dotenv import load_dotenv
from telegram import Location, Update
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    filters,
)

load_dotenv()

logging.basicConfig(
    format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger("trip_trace_bot")

# httpx (used internally by python-telegram-bot for polling) logs one INFO
# line per getUpdates call — noise unrelated to our own data, silenced here.
logging.getLogger("httpx").setLevel(logging.WARNING)

TELEGRAM_BOT_TOKEN = os.environ["TELEGRAM_BOT_TOKEN"]
ALLOWED_TELEGRAM_USER_ID = int(os.environ["ALLOWED_TELEGRAM_USER_ID"])

# API_BASE_URL = os.environ.get("API_BASE_URL", "https://trip-trace-api.onrender.com")
# API_EMAIL = os.environ["API_EMAIL"]
# API_PASSWORD = os.environ["API_PASSWORD"]

STATUS_NONE = "NONE"
STATUS_CREATED = "CREATED"
STATUS_IN_PROGRESS = "IN_PROGRESS"

# In-memory session state — fine for a single-user bot running as one
# process.
# api_token: Optional[str] = None
active_trip_id: Optional[str] = None
active_trip_status: str = STATUS_NONE
collected_points: list[dict] = []


def is_authorized(update: Update) -> bool:
    return (
        update.effective_user is not None
        and update.effective_user.id == ALLOWED_TELEGRAM_USER_ID
    )


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def extract_location(update: Update) -> Optional[Location]:
    # Live Location updates arrive as edited_message, not a new message —
    # a plain MessageHandler already listens to both by default in PTB 20+,
    # but the location itself lives on whichever one is set.
    message = update.message or update.edited_message
    return message.location if message else None


# --- trip-trace-api calls — commented out for now. We're testing that
# Telegram location data reaches the bot correctly first; uncomment these
# (and the API_* env vars above, and post_init below) once that's confirmed
# and we're ready to wire the bot up to the real API again.

# async def login_to_api() -> str:
#     logger.info("Logging in to trip-trace-api")
#     async with httpx.AsyncClient() as client:
#         response = await client.post(
#             f"{API_BASE_URL}/api/v1/auth/login",
#             data={"username": API_EMAIL, "password": API_PASSWORD},
#         )
#         response.raise_for_status()
#         token = response.json()["access_token"]
#     logger.info("Login successful")
#     return token


# async def create_trip(lat: float, lng: float, destination: str) -> dict:
#     logger.info("Creating trip to %s", destination)
#     async with httpx.AsyncClient() as client:
#         response = await client.post(
#             f"{API_BASE_URL}/api/v1/trips",
#             headers={"Authorization": f"Bearer {api_token}"},
#             json={
#                 "origin_name": "Ubicacion actual (Telegram)",
#                 "origin_lat": lat,
#                 "origin_lng": lng,
#                 "destination_name": destination,
#                 "destination_lat": lat,
#                 "destination_lng": lng,
#             },
#         )
#         response.raise_for_status()
#         return response.json()


# async def send_gps_points(trip_id: str, points: list[dict]) -> None:
#     logger.info("Sending %d GPS points for trip %s", len(points), trip_id)
#     async with httpx.AsyncClient() as client:
#         response = await client.post(
#             f"{API_BASE_URL}/api/v1/trips/{trip_id}/gps-points",
#             headers={"Authorization": f"Bearer {api_token}"},
#             json=points,
#         )
#         response.raise_for_status()


# async def patch_trip(trip_id: str, payload: dict) -> None:
#     async with httpx.AsyncClient() as client:
#         response = await client.patch(
#             f"{API_BASE_URL}/api/v1/trips/{trip_id}",
#             headers={"Authorization": f"Bearer {api_token}"},
#             json=payload,
#         )
#         response.raise_for_status()


# async def finalize_trip(trip_id: str) -> dict:
#     async with httpx.AsyncClient() as client:
#         response = await client.post(
#             f"{API_BASE_URL}/api/v1/trips/{trip_id}/finalize",
#             headers={"Authorization": f"Bearer {api_token}"},
#         )
#         response.raise_for_status()
#         return response.json()


async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not is_authorized(update):
        await update.message.reply_text("No autorizado.")
        return
    await update.message.reply_text(
        "TripTrace bot listo (modo prueba — todavia no envia nada a la API).\n\n"
        "/nuevo_viaje <destino> - simula crear un viaje con tu ubicacion actual como origen\n"
        "/iniciar - arranca a grabar los puntos GPS que lleguen\n"
        "/finalizar - corta la grabacion e imprime los puntos acumulados"
    )


async def new_trip_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    global active_trip_status

    if not is_authorized(update):
        return
    if not context.args:
        await update.message.reply_text("Uso: /nuevo_viaje <destino>")
        return

    context.user_data["pending_destination"] = " ".join(context.args)
    await update.message.reply_text(
        "Compartí tu ubicación actual (clip 📎 → Ubicación) para usarla como origen."
    )


async def location_received(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    global active_trip_id, active_trip_status

    if not is_authorized(update):
        return

    location = extract_location(update)
    if location is None:
        return

    is_live = location.live_period is not None
    logger.info(
        "Location received (live=%s): lat=%s lng=%s accuracy=%s heading=%s "
        "live_period=%s proximity_alert_radius=%s",
        is_live,
        location.latitude,
        location.longitude,
        location.horizontal_accuracy,
        location.heading,
        location.live_period,
        location.proximity_alert_radius,
    )

    if not is_live and "pending_destination" in context.user_data:
        destination = context.user_data.pop("pending_destination")
        # trip = await create_trip(location.latitude, location.longitude, destination)
        # active_trip_id = trip["id"]
        active_trip_id = "local-test-trip"
        active_trip_status = STATUS_CREATED
        logger.info(
            "Would create trip to %s (origin lat=%s lng=%s)",
            destination,
            location.latitude,
            location.longitude,
        )
        await update.message.reply_text(
            f"[Simulado] Viaje creado hacia '{destination}'. Corré /iniciar cuando arranques."
        )
        return

    if is_live and active_trip_status == STATUS_IN_PROGRESS:
        collected_points.append(
            {
                "lat": location.latitude,
                "lng": location.longitude,
                "accuracy": location.horizontal_accuracy,
                "heading": location.heading,
                "recorded_at": now_iso(),
            }
        )
        logger.info(
            "Point #%d stored for trip %s (not sent to the API yet)",
            len(collected_points),
            active_trip_id,
        )


async def start_trip_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    global active_trip_status

    if not is_authorized(update):
        return
    if active_trip_status == STATUS_NONE:
        await update.message.reply_text("No hay ningún viaje creado. Usá /nuevo_viaje primero.")
        return
    if active_trip_status == STATUS_IN_PROGRESS:
        await update.message.reply_text("El viaje ya está en curso.")
        return

    active_trip_status = STATUS_IN_PROGRESS
    collected_points.clear()
    # await patch_trip(active_trip_id, {"status": "IN_PROGRESS", "started_at": now_iso()})
    logger.info("Trip %s marked IN_PROGRESS — now recording points", active_trip_id)
    await update.message.reply_text(
        "[Simulado] Viaje iniciado, grabando puntos. Compartí tu Ubicación en tiempo real "
        "(clip 📎 → Ubicación → Compartir ubicación en tiempo real)."
    )


async def finish_trip_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    global active_trip_id, active_trip_status

    if not is_authorized(update):
        return
    if active_trip_status != STATUS_IN_PROGRESS:
        await update.message.reply_text("No hay ningún viaje en curso.")
        return

    trip_id = active_trip_id
    logger.info("Trip %s finished — %d points collected:", trip_id, len(collected_points))
    for index, point in enumerate(collected_points, start=1):
        logger.info("  #%d %s", index, point)

    # await patch_trip(trip_id, {"status": "COMPLETED", "ended_at": now_iso()})
    # await send_gps_points(trip_id, collected_points)
    # stats = await finalize_trip(trip_id)

    await update.message.reply_text(
        f"[Simulado] Viaje finalizado. Se grabaron {len(collected_points)} puntos "
        f"(mirá la terminal para el detalle — todavía no se mandaron a la API)."
    )

    active_trip_id = None
    active_trip_status = STATUS_NONE
    collected_points.clear()


# async def post_init(application: Application) -> None:
#     global api_token
#     api_token = await login_to_api()


def main() -> None:
    application = (
        Application.builder()
        .token(TELEGRAM_BOT_TOKEN)
        # .post_init(post_init)
        .build()
    )

    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(CommandHandler("nuevo_viaje", new_trip_command))
    application.add_handler(CommandHandler("iniciar", start_trip_command))
    application.add_handler(CommandHandler("finalizar", finish_trip_command))
    application.add_handler(MessageHandler(filters.LOCATION, location_received))

    logger.info("Starting bot (polling, trip-trace-api calls disabled for now)")
    application.run_polling()


if __name__ == "__main__":
    main()

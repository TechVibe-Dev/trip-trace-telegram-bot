"""Telegram bot for TripTrace — a lightweight alternative client to the
Android app, using Telegram's own Live Location feature for GPS tracking
instead of a native foreground service.
"""

import logging
import os
from datetime import datetime, timezone
from typing import Optional

import httpx
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

TELEGRAM_BOT_TOKEN = os.environ["TELEGRAM_BOT_TOKEN"]
ALLOWED_TELEGRAM_USER_ID = int(os.environ["ALLOWED_TELEGRAM_USER_ID"])
API_BASE_URL = os.environ.get("API_BASE_URL", "https://trip-trace-api.onrender.com")
API_EMAIL = os.environ["API_EMAIL"]
API_PASSWORD = os.environ["API_PASSWORD"]

# In-memory session state — fine for a single-user bot running as one
# process. Would need a real store (DB, or at least a file) to survive
# restarts or support more than one concurrent trip/user.
api_token: Optional[str] = None
active_trip_id: Optional[str] = None


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


async def login_to_api() -> str:
    logger.info("Logging in to trip-trace-api")
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{API_BASE_URL}/api/v1/auth/login",
            data={"username": API_EMAIL, "password": API_PASSWORD},
        )
        response.raise_for_status()
        token = response.json()["access_token"]
    logger.info("Login successful")
    return token


async def create_trip(lat: float, lng: float, destination: str) -> dict:
    logger.info("Creating trip to %s", destination)
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{API_BASE_URL}/api/v1/trips",
            headers={"Authorization": f"Bearer {api_token}"},
            json={
                "origin_name": "Ubicacion actual (Telegram)",
                "origin_lat": lat,
                "origin_lng": lng,
                "destination_name": destination,
                # Placeholder until geocoding exists — same gap as the
                # Android app (android#23). Destination text is stored, but
                # not resolved to real coordinates yet.
                "destination_lat": lat,
                "destination_lng": lng,
            },
        )
        response.raise_for_status()
        return response.json()


async def send_gps_point(trip_id: str, lat: float, lng: float) -> None:
    logger.info("Sending GPS point for trip %s", trip_id)
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{API_BASE_URL}/api/v1/trips/{trip_id}/gps-points",
            headers={"Authorization": f"Bearer {api_token}"},
            json=[{"lat": lat, "lng": lng, "recorded_at": now_iso()}],
        )
        response.raise_for_status()


async def patch_trip(trip_id: str, payload: dict) -> None:
    async with httpx.AsyncClient() as client:
        response = await client.patch(
            f"{API_BASE_URL}/api/v1/trips/{trip_id}",
            headers={"Authorization": f"Bearer {api_token}"},
            json=payload,
        )
        response.raise_for_status()


async def finalize_trip(trip_id: str) -> dict:
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{API_BASE_URL}/api/v1/trips/{trip_id}/finalize",
            headers={"Authorization": f"Bearer {api_token}"},
        )
        response.raise_for_status()
        return response.json()


async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not is_authorized(update):
        await update.message.reply_text("No autorizado.")
        return
    await update.message.reply_text(
        "TripTrace bot listo.\n\n"
        "/nuevo_viaje <destino> - crea un viaje con tu ubicacion actual como origen\n"
        "/iniciar - marca el viaje como en curso\n"
        "/finalizar - termina el viaje activo y calcula las metricas"
    )


async def new_trip_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
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
    global active_trip_id

    if not is_authorized(update):
        return

    location = extract_location(update)
    if location is None:
        return

    is_live = location.live_period is not None

    if not is_live and "pending_destination" in context.user_data:
        destination = context.user_data.pop("pending_destination")
        trip = await create_trip(location.latitude, location.longitude, destination)
        active_trip_id = trip["id"]
        await update.message.reply_text(
            f"Viaje creado (id {active_trip_id}). Corré /iniciar cuando arranques."
        )
        return

    if is_live and active_trip_id:
        await send_gps_point(active_trip_id, location.latitude, location.longitude)


async def start_trip_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not is_authorized(update):
        return
    if not active_trip_id:
        await update.message.reply_text("No hay ningún viaje creado. Usá /nuevo_viaje primero.")
        return

    await patch_trip(active_trip_id, {"status": "IN_PROGRESS", "started_at": now_iso()})
    await update.message.reply_text(
        "Viaje iniciado. Ahora compartí tu Ubicación en tiempo real "
        "(clip 📎 → Ubicación → Compartir ubicación en tiempo real)."
    )


async def finish_trip_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    global active_trip_id

    if not is_authorized(update):
        return
    if not active_trip_id:
        await update.message.reply_text("No hay ningún viaje activo.")
        return

    trip_id = active_trip_id
    await patch_trip(trip_id, {"status": "COMPLETED", "ended_at": now_iso()})
    stats = await finalize_trip(trip_id)
    active_trip_id = None

    await update.message.reply_text(
        f"Viaje finalizado.\n"
        f"Distancia: {stats.get('distance_km')} km\n"
        f"Velocidad promedio: {stats.get('avg_speed')} km/h\n"
        f"Velocidad maxima: {stats.get('max_speed')} km/h"
    )


async def post_init(application: Application) -> None:
    global api_token
    api_token = await login_to_api()


def main() -> None:
    application = (
        Application.builder()
        .token(TELEGRAM_BOT_TOKEN)
        .post_init(post_init)
        .build()
    )

    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(CommandHandler("nuevo_viaje", new_trip_command))
    application.add_handler(CommandHandler("iniciar", start_trip_command))
    application.add_handler(CommandHandler("finalizar", finish_trip_command))
    application.add_handler(MessageHandler(filters.LOCATION, location_received))

    logger.info("Starting bot (polling)")
    application.run_polling()


if __name__ == "__main__":
    main()

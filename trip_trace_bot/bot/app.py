"""Builds the python-telegram-bot Application and wires every handler."""

import logging

from telegram import BotCommand, Update
from telegram.ext import Application, ContextTypes, MessageHandler, filters

from trip_trace_bot.api import TripTraceClient
from trip_trace_bot.bot.context import API_CLIENT_KEY
from trip_trace_bot.bot.errors import on_error
from trip_trace_bot.bot.handlers import MODULES
from trip_trace_bot.config import Config

logger = logging.getLogger(__name__)

# Shown in Telegram's command menu (the "/" button).
COMMANDS = [
    BotCommand("ayuda", "Qué puede hacer el bot"),
    BotCommand("estado", "Verificar la conexión con TripTrace"),
]


async def _log_ignored(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user = update.effective_user
    if user is not None:
        logger.info("Ignored message from user %s (@%s)", user.id, user.username)


def build_application(config: Config) -> Application:
    allowed = filters.User(user_id=config.allowed_user_ids)

    async def post_init(application: Application) -> None:
        application.bot_data[API_CLIENT_KEY] = TripTraceClient(
            base_url=config.api_url,
            username=config.api_username,
            password=config.api_password,
            timeout_seconds=config.api_timeout_seconds,
        )
        await application.bot.set_my_commands(COMMANDS)

    async def post_shutdown(application: Application) -> None:
        client = application.bot_data.get(API_CLIENT_KEY)
        if client is not None:
            await client.close()

    application = (
        Application.builder()
        .token(config.telegram_bot_token)
        .post_init(post_init)
        .post_shutdown(post_shutdown)
        .build()
    )

    for module in MODULES:
        module.register(application, allowed)
    # Anyone outside the allowlist gets no reply, only a log line.
    application.add_handler(MessageHandler(~allowed, _log_ignored), group=1)
    application.add_error_handler(on_error)
    return application

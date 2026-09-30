"""Global error handler: logs the failure and tells the user in plain words."""

import logging

from telegram import Update
from telegram.ext import ContextTypes

from trip_trace_bot.api import ApiError, ApiUnavailableError
from trip_trace_bot.bot import messages

logger = logging.getLogger(__name__)


def reply_for(error: BaseException | None) -> str:
    if isinstance(error, ApiUnavailableError):
        return messages.API_UNAVAILABLE
    if isinstance(error, ApiError):
        return messages.API_ERROR.format(status_code=error.status_code)
    return messages.UNEXPECTED_ERROR


async def on_error(update: object, context: ContextTypes.DEFAULT_TYPE) -> None:
    logger.error("Error while handling an update", exc_info=context.error)
    if isinstance(update, Update) and update.effective_message is not None:
        await update.effective_message.reply_text(reply_for(context.error))

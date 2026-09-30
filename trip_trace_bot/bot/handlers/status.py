from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes, filters

from trip_trace_bot.bot import messages
from trip_trace_bot.bot.context import api_client


async def status_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    # API errors are turned into a reply by the global error handler.
    me = await api_client(context).get_me()
    await update.effective_message.reply_text(
        messages.STATUS_OK.format(username=me.get("username") or me.get("email"))
    )


def register(application: Application, allowed: filters.BaseFilter) -> None:
    application.add_handler(CommandHandler("estado", status_command, filters=allowed))

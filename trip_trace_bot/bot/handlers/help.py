from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes, filters

from trip_trace_bot.bot import messages


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.effective_message.reply_text(messages.HELP)


def register(application: Application, allowed: filters.BaseFilter) -> None:
    application.add_handler(CommandHandler(["start", "ayuda"], help_command, filters=allowed))

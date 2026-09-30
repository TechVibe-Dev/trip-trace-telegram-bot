"""Typed access to the objects shared by every handler."""

from telegram.ext import ContextTypes

from trip_trace_bot.api import TripTraceClient

API_CLIENT_KEY = "api_client"


def api_client(context: ContextTypes.DEFAULT_TYPE) -> TripTraceClient:
    return context.bot_data[API_CLIENT_KEY]

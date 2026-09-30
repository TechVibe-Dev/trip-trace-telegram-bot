"""One module per feature. Each exposes `register(application, allowed)`."""

from trip_trace_bot.bot.handlers import help, status

MODULES = (help, status)

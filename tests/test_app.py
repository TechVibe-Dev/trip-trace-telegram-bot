from telegram.ext import CommandHandler

from trip_trace_bot.bot.app import COMMANDS, build_application
from trip_trace_bot.config import load_config


def test_every_menu_command_has_a_handler():
    config = load_config(
        {
            "TELEGRAM_BOT_TOKEN": "123:abc",
            "ALLOWED_TELEGRAM_USER_IDS": "111",
            "API_USERNAME": "joaquin",
            "API_PASSWORD": "secret",
        }
    )

    application = build_application(config)

    handled = {
        command
        for handlers in application.handlers.values()
        for handler in handlers
        if isinstance(handler, CommandHandler)
        for command in handler.commands
    }
    assert {command.command for command in COMMANDS} <= handled

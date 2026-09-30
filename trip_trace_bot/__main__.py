"""Entry point: `python -m trip_trace_bot`."""

import logging
import sys

from trip_trace_bot import __version__
from trip_trace_bot.bot.app import build_application
from trip_trace_bot.config import ConfigError, load_config, load_env_file


def main() -> int:
    load_env_file()
    try:
        config = load_config()
    except ConfigError as exc:
        print(f"Configuration error: {exc}", file=sys.stderr)
        return 1

    logging.basicConfig(
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
        level=config.log_level,
    )
    # httpx logs every getUpdates poll at INFO; keep only warnings.
    logging.getLogger("httpx").setLevel(logging.WARNING)

    logging.getLogger("trip_trace_bot").info(
        "Starting trip-trace-telegram-bot %s (api=%s, allowed users=%d)",
        __version__,
        config.api_url,
        len(config.allowed_user_ids),
    )
    build_application(config).run_polling()
    return 0


if __name__ == "__main__":
    sys.exit(main())

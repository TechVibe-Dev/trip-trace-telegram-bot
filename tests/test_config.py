import pytest

from trip_trace_bot.config import DEFAULT_API_URL, ConfigError, load_config

BASE_ENV = {
    "TELEGRAM_BOT_TOKEN": "123:abc",
    "ALLOWED_TELEGRAM_USER_IDS": "111, 222",
    "API_USERNAME": "joaquin",
    "API_PASSWORD": "secret",
}


def test_loads_minimal_config_with_defaults():
    config = load_config(BASE_ENV)

    assert config.allowed_user_ids == frozenset({111, 222})
    assert config.api_url == DEFAULT_API_URL
    assert config.api_timeout_seconds == 30
    assert config.log_level == "INFO"


def test_strips_trailing_slash_from_api_url():
    config = load_config({**BASE_ENV, "API_URL": "http://localhost:8000/"})

    assert config.api_url == "http://localhost:8000"


@pytest.mark.parametrize(
    "name", ["TELEGRAM_BOT_TOKEN", "ALLOWED_TELEGRAM_USER_IDS", "API_USERNAME", "API_PASSWORD"]
)
def test_missing_required_variable_fails(name):
    env = {**BASE_ENV, name: " "}

    with pytest.raises(ConfigError, match=name):
        load_config(env)


def test_rejects_non_numeric_user_id():
    with pytest.raises(ConfigError, match="numeric"):
        load_config({**BASE_ENV, "ALLOWED_TELEGRAM_USER_IDS": "111,@joaquin"})


@pytest.mark.parametrize("value", ["0", "-5", "abc"])
def test_rejects_invalid_timeout(value):
    with pytest.raises(ConfigError, match="API_TIMEOUT_SECONDS"):
        load_config({**BASE_ENV, "API_TIMEOUT_SECONDS": value})


def test_rejects_unknown_log_level():
    with pytest.raises(ConfigError, match="LOG_LEVEL"):
        load_config({**BASE_ENV, "LOG_LEVEL": "verbose"})

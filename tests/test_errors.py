from trip_trace_bot.api import ApiError, ApiUnavailableError
from trip_trace_bot.bot import messages
from trip_trace_bot.bot.errors import reply_for


def test_unavailable_api_gets_a_retry_later_reply():
    assert reply_for(ApiUnavailableError("timeout")) == messages.API_UNAVAILABLE


def test_api_error_reply_includes_the_status_code():
    assert "503" in reply_for(ApiError(503, "Service Unavailable"))


def test_anything_else_gets_a_generic_reply():
    assert reply_for(RuntimeError("boom")) == messages.UNEXPECTED_ERROR

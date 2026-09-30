import httpx
import pytest

from trip_trace_bot.api import ApiError, ApiUnavailableError, TripTraceClient


class FakeApi:
    """Minimal stand-in for trip-trace-api's auth endpoints."""

    def __init__(self) -> None:
        self.logins = 0
        self.valid_token: str | None = None
        self.expire_next_request = False

    def handler(self, request: httpx.Request) -> httpx.Response:
        if request.url.path == "/api/v1/auth/login":
            self.logins += 1
            self.valid_token = f"token-{self.logins}"
            return httpx.Response(200, json={"access_token": self.valid_token})
        if request.url.path == "/api/v1/auth/me":
            if self.expire_next_request:
                self.expire_next_request = False
                return httpx.Response(401, json={"detail": "Token expired"})
            if request.headers.get("Authorization") != f"Bearer {self.valid_token}":
                return httpx.Response(401, json={"detail": "Invalid token"})
            return httpx.Response(200, json={"username": "joaquin", "email": "j@example.com"})
        return httpx.Response(404, json={"detail": "Not Found"})


def make_client(api: FakeApi) -> TripTraceClient:
    return TripTraceClient(
        base_url="http://api.test",
        username="joaquin",
        password="secret",
        transport=httpx.MockTransport(api.handler),
    )


async def test_logs_in_once_and_reuses_the_token():
    api = FakeApi()
    client = make_client(api)

    await client.get_me()
    me = await client.get_me()

    assert me["username"] == "joaquin"
    assert api.logins == 1


async def test_logs_in_again_when_the_token_expires():
    api = FakeApi()
    client = make_client(api)
    await client.get_me()

    api.expire_next_request = True
    me = await client.get_me()

    assert me["username"] == "joaquin"
    assert api.logins == 2


async def test_login_failure_raises_api_error():
    client = TripTraceClient(
        base_url="http://api.test",
        username="joaquin",
        password="wrong",
        transport=httpx.MockTransport(
            lambda request: httpx.Response(400, json={"detail": "Invalid credentials"})
        ),
    )

    with pytest.raises(ApiError) as exc_info:
        await client.get_me()

    assert exc_info.value.status_code == 400
    assert exc_info.value.detail == "Invalid credentials"


async def test_network_error_raises_api_unavailable():
    def fail(request: httpx.Request) -> httpx.Response:
        raise httpx.ConnectError("connection refused", request=request)

    client = TripTraceClient(
        base_url="http://api.test",
        username="joaquin",
        password="secret",
        transport=httpx.MockTransport(fail),
    )

    with pytest.raises(ApiUnavailableError):
        await client.get_me()

"""HTTP client for trip-trace-api. The only module that knows the API's URLs."""

import logging
from typing import Any

import httpx

logger = logging.getLogger(__name__)


class ApiError(Exception):
    """The API answered with an error status."""

    def __init__(self, status_code: int, detail: str) -> None:
        super().__init__(f"API error {status_code}: {detail}")
        self.status_code = status_code
        self.detail = detail


class ApiUnavailableError(Exception):
    """The API could not be reached (network error or timeout)."""


class TripTraceClient:
    """Logs in once and reuses the token.

    /auth/login is rate limited (3 per minute), so the client only logs in
    again when a request comes back 401 (expired token), never per request.
    """

    def __init__(
        self,
        base_url: str,
        username: str,
        password: str,
        timeout_seconds: float = 30.0,
        transport: httpx.AsyncBaseTransport | None = None,
    ) -> None:
        self._username = username
        self._password = password
        self._token: str | None = None
        self._http = httpx.AsyncClient(
            base_url=base_url, timeout=timeout_seconds, transport=transport
        )

    async def close(self) -> None:
        await self._http.aclose()

    async def health(self) -> bool:
        try:
            response = await self._http.get("/health")
        except httpx.HTTPError as exc:
            raise ApiUnavailableError(str(exc)) from exc
        return response.status_code == 200

    async def get_me(self) -> dict[str, Any]:
        return await self._request("GET", "/api/v1/auth/me")

    async def _login(self) -> None:
        logger.info("Logging in to trip-trace-api as %s", self._username)
        try:
            response = await self._http.post(
                "/api/v1/auth/login",
                data={"username": self._username, "password": self._password},
            )
        except httpx.HTTPError as exc:
            raise ApiUnavailableError(str(exc)) from exc
        if response.status_code != 200:
            raise ApiError(response.status_code, _detail(response))
        self._token = response.json()["access_token"]

    async def _request(self, method: str, path: str, **kwargs: Any) -> Any:
        if self._token is None:
            await self._login()
        response = await self._send(method, path, **kwargs)
        if response.status_code == 401:
            await self._login()
            response = await self._send(method, path, **kwargs)
        if response.status_code >= 400:
            raise ApiError(response.status_code, _detail(response))
        if response.status_code == 204:
            return None
        return response.json()

    async def _send(self, method: str, path: str, **kwargs: Any) -> httpx.Response:
        headers = {"Authorization": f"Bearer {self._token}"}
        try:
            return await self._http.request(method, path, headers=headers, **kwargs)
        except httpx.HTTPError as exc:
            raise ApiUnavailableError(str(exc)) from exc


def _detail(response: httpx.Response) -> str:
    try:
        return str(response.json().get("detail", response.text))
    except ValueError:
        return response.text

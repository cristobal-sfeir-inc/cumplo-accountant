"""HTTP client for Cumplo's Global API."""

from http import HTTPMethod
from logging import getLogger

import requests
from cumplo_common.models import Credentials, Session
from pydantic import BaseModel, Field
from requests.exceptions import HTTPError, JSONDecodeError
from retry import retry

from cumplo_accountant.utils.constants import (
    CUMPLO_BALANCE_URL,
    CUMPLO_COMPANY_URL,
    CUMPLO_GLOBAL_API,
    CUMPLO_LOGIN_URL,
)

logger = getLogger(__name__)


class CumploCompany(BaseModel):
    """Cumplo company model."""

    id: int = Field(...)
    nin: str = Field(alias="numero_identificador")


class CumploGlobalAPI:
    """Class to interact with Cumplo's Global API."""

    url = CUMPLO_GLOBAL_API

    @classmethod
    def _request(
        cls,
        method: HTTPMethod,
        endpoint: str,
        payload: dict | None = None,
        headers: dict | None = None,
    ) -> requests.Response:
        """
        Make a request to Cumplo's Global API.

        Args:
            method (HTTPMethod): HTTP method to use
            endpoint (str): Endpoint to call
            payload (dict): Payload to send
            headers (dict): Headers to send

        Returns:
            requests.Response: Response from the API

        """
        return requests.request(method=method, url=f"{cls.url}{endpoint}", json=payload, headers=headers)

    @classmethod
    @retry((JSONDecodeError, HTTPError, KeyError), tries=3, delay=1)
    def login(cls, email: str, password: str) -> tuple[str, int]:
        """
        Login to Cumplo's Global API.

        Args:
            email (str): The email to use
            password (str): The password to use

        Returns:
            tuple[str, int]: The JWT token and the user ID

        """
        payload = {"identifier": email, "password": password}
        response = cls._request(HTTPMethod.POST, endpoint=CUMPLO_LOGIN_URL, payload=payload)
        response.raise_for_status()

        content = response.json()
        return content["jwt"], content["user"]["id"]

    @classmethod
    @retry((JSONDecodeError, HTTPError, KeyError), tries=3, delay=1)
    def get_balance(cls, session: Session, credentials: Credentials) -> int:
        """Get the balance of the user."""
        endpoint = CUMPLO_BALANCE_URL.format(company_id=credentials.company_id)
        response = cls._request(HTTPMethod.GET, endpoint=endpoint, headers=session.headers)

        response.raise_for_status()
        balances = response.json()["data"]["attributes"]["saldos"]["resumen"]
        return balances["saldo_cumplo"]

    @classmethod
    # @retry((JSONDecodeError, HTTPError, KeyError), tries=3, delay=1)
    def get_company(cls, session: Session, cumplo_user_id: int) -> CumploCompany:
        """Get the company associated with the user."""
        endpoint = CUMPLO_COMPANY_URL.format(cumplo_user_id=cumplo_user_id)
        response = cls._request(HTTPMethod.GET, endpoint=endpoint, headers=session.headers)
        response.raise_for_status()

        content = response.json()["data"][0]
        return CumploCompany(id=content["id"], **content["attributes"])

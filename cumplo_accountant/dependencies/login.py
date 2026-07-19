"""Login dependency that authenticates users against Cumplo's API."""

from http import HTTPStatus
from logging import getLogger
from typing import cast

from cumplo_common.database import firestore
from cumplo_common.models import Session, User
from fastapi.exceptions import HTTPException
from fastapi.requests import Request

from cumplo_accountant.integrations import CumploGlobalAPI

logger = getLogger(__name__)


def login(request: Request) -> None:
    """
    Login the user and save the session in the request state.

    Args:
        request (Request): The request to authenticate

    Raises:
        HTTPException: When the user has no Cumplo credentials configured

    """
    user = cast(User, request.state.user)
    if not user.credentials or not user.credentials.valid:
        raise HTTPException(HTTPStatus.BAD_REQUEST, detail="No valid Cumplo credentials configured")

    if user.session and not user.session.has_expired:
        logger.debug(f"User {user.id} already has a valid session")
        return

    logger.debug(f"Logging in user {user.id}")
    try:
        token, _ = CumploGlobalAPI.login(user.credentials.email, user.credentials.decrypted_password)
    except Exception as exception:
        logger.warning(f"User {user.id} credentials are invalid: {exception}")
        user.credentials.valid = False
        firestore.client.users.update(user, "credentials")
        raise HTTPException(HTTPStatus.BAD_REQUEST, detail="Invalid credentials") from exception

    user.session = Session(token=token)

    firestore.client.users.update(user, "session")
    logger.debug(f"User {user.id} logged in successfully")

    request.state.user = user

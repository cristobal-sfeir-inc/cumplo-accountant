"""Router for credentials management endpoints."""

from http import HTTPStatus
from logging import getLogger
from typing import cast

from cumplo_common.database import firestore
from cumplo_common.models import Credentials, Session, User
from fastapi import APIRouter, HTTPException
from fastapi.requests import Request
from pydantic import BaseModel

from cumplo_accountant.integrations import CumploGlobalAPI

logger = getLogger(__name__)


router = APIRouter(prefix="/credentials")


class CredentialsUpdate(BaseModel):
    """Credentials update model."""

    email: str
    password: str


@router.put("", status_code=HTTPStatus.CREATED)
def _upsert_credentials(request: Request, payload: CredentialsUpdate) -> None:
    """Upsert the user's credentials."""
    user = cast(User, request.state.user)
    logger.info(f"Upserting credentials for user {user.id}")

    if (
        user.credentials
        and user.credentials.email == payload.email
        and user.credentials.decrypted_password == payload.password
    ):
        logger.info(f"User {user.id} credentials are already set. Nothing to update.")
        return

    try:
        token, user_id = CumploGlobalAPI.login(email=payload.email, password=payload.password)
    except Exception as exception:
        logger.warning(f"User {user.id} credentials are invalid: {exception}")
        raise HTTPException(status_code=HTTPStatus.BAD_REQUEST, detail="Invalid credentials") from exception

    logger.info(f"User {user.id} logged in successfully")
    user.session = Session(token=token)

    logger.info(f"Getting company for user {user.id}")
    company = CumploGlobalAPI.get_company(session=user.session, cumplo_user_id=user_id)

    user.credentials = Credentials(
        email=payload.email,
        password=payload.password,
        company_nin=company.nin,
        company_id=str(company.id),
        user_id=str(user_id),
    )
    firestore.client.users.update(user, "credentials")
    firestore.client.users.update(user, "session")

    logger.info(f"Credentials for user {user.id} upserted successfully")

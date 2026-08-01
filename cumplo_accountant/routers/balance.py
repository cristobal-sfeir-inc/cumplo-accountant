"""Router for balance retrieval endpoints."""

from enum import StrEnum
from http import HTTPStatus
from logging import getLogger
from typing import cast

from cumplo_common.database import firestore
from cumplo_common.models import Balance
from fastapi import APIRouter
from fastapi.requests import Request

from cumplo_accountant.integrations import CumploGlobalAPI
from cumplo_accountant.models import LoggedUser

logger = getLogger(__name__)


router = APIRouter(prefix="/balance")


class CumploInvestmentStatus(StrEnum):
    """Cumplo investment status."""

    ACTIVE = "ACTIVADA"
    OVERDUE = "MORA"
    PENDING = "RECAUDACION"
    PAID = "PAGADA"


@router.get("", status_code=HTTPStatus.OK)
def _get_balance(request: Request) -> int:
    """Return the balance of the user."""
    user = cast(LoggedUser, request.state.user)

    if not user.balance or user.balance.has_expired:
        logger.info(f"User {user.id} balance has expired. Retrieving new balance")
        balance = CumploGlobalAPI.get_balance(session=user.session, credentials=user.credentials)

        user.balance = Balance(amount=balance)
        firestore.client.users.update(user, attribute="balance")

    return user.balance.amount


@router.post("/retrieve", status_code=HTTPStatus.OK)
def _retrieve_balance(request: Request) -> None:
    """Retrieve the balance of the user and update the user's balance in Firestore."""
    user = cast(LoggedUser, request.state.user)
    balance = CumploGlobalAPI.get_balance(session=user.session, credentials=user.credentials)

    user.balance = Balance(amount=balance)
    firestore.client.users.update(user, attribute="balance")

"""Authentication service for Cumplo session management."""

from logging import getLogger

from cumplo_common.database import firestore
from cumplo_common.models import Session

from cumplo_accountant.integrations.cumplo import CumploGlobalAPI
from cumplo_accountant.models import LoggedUser

logger = getLogger(__name__)


class AuthenticationService:
    """Service to handle authentication."""

    @staticmethod
    def login(user: LoggedUser) -> Session:
        """Login to Cumplo's Global API."""
        if user.session and not user.session.has_expired:
            logger.debug(f"User {user.id} already has a valid session")
            return user.session

        logger.debug(f"Logging in user {user.id}")
        token, _ = CumploGlobalAPI.login(user.credentials)  # type: ignore  # TODO(NOT-XX): fix wrong call signature or remove dead code
        user.session = Session(token=token)

        firestore.client.users.update(user, "session")
        logger.debug(f"User {user.id} logged in successfully")

        return user.session

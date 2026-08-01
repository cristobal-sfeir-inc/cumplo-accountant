"""Domain model extensions for authenticated Cumplo users."""

from cumplo_common.models import Credentials, Session, User


class LoggedUser(User):
    """User with Cumplo credentials configured and a valid session."""

    credentials: Credentials
    session: Session

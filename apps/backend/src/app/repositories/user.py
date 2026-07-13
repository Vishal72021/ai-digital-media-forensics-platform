"""User repository."""

from sqlalchemy.orm import Session


class UserRepository:
    """Repository responsible for user persistence."""

    def __init__(self, session: Session) -> None:
        """Initialize the repository.

        Args:
            session: SQLAlchemy database session.
        """
        self._session = session

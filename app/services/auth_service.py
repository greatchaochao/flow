"""
Authentication service for user management.
"""

from typing import Optional
from sqlalchemy.orm import Session
from app.database.models import User
from app.utils.security import verify_password, hash_password


class AuthService:
    """Service for user authentication."""

    def __init__(self, db: Session):
        self.db = db

    def authenticate(self, email: str, password: str) -> Optional[User]:
        """
        Authenticate user with email and password.

        Args:
            email: User email
            password: Plain text password

        Returns:
            User object if authentication successful, None otherwise
        """
        user = self.db.query(User).filter(User.email == email).first()

        if not user:
            return None

        if not user.is_active:
            return None

        if not verify_password(password, user.password_hash):
            return None

        return user

    def get_user_by_id(self, user_id: int) -> Optional[User]:
        """
        Get user by ID.

        Args:
            user_id: User ID

        Returns:
            User object if found, None otherwise
        """
        return self.db.query(User).filter(User.id == user_id).first()

    def get_user_by_email(self, email: str) -> Optional[User]:
        """
        Get user by email.

        Args:
            email: User email

        Returns:
            User object if found, None otherwise
        """
        return self.db.query(User).filter(User.email == email).first()

    def create_user(
        self,
        email: str,
        password: str,
        full_name: str,
        role: str,
        company_id: int,
    ) -> User:
        """
        Create a new user.

        Args:
            email: User email
            password: Plain text password
            full_name: User's full name
            role: User role (admin, maker, approver)
            company_id: Company ID

        Returns:
            Created User object
        """
        password_hash = hash_password(password)

        user = User(
            email=email,
            password_hash=password_hash,
            full_name=full_name,
            role=role,
            company_id=company_id,
            is_active=True,
        )

        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)

        return user

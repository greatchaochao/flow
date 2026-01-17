"""
User repository for database operations.
"""

from typing import Optional, List
from sqlalchemy.orm import Session
from app.database.models import User


class UserRepository:
    """Repository for user database operations."""

    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, user_id: int) -> Optional[User]:
        """
        Get user by ID.

        Args:
            user_id: User ID

        Returns:
            User object if found, None otherwise
        """
        return self.db.query(User).filter(User.id == user_id).first()

    def get_by_email(self, email: str) -> Optional[User]:
        """
        Get user by email.

        Args:
            email: User email

        Returns:
            User object if found, None otherwise
        """
        return self.db.query(User).filter(User.email == email).first()

    def get_all(self) -> List[User]:
        """
        Get all users.

        Returns:
            List of all users
        """
        return self.db.query(User).all()

    def get_by_company(self, company_id: int) -> List[User]:
        """
        Get all users for a company.

        Args:
            company_id: Company ID

        Returns:
            List of users
        """
        return self.db.query(User).filter(User.company_id == company_id).all()

    def create(self, user_data: dict) -> User:
        """
        Create a new user.

        Args:
            user_data: Dictionary containing user data

        Returns:
            Created user object
        """
        user = User(**user_data)
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        return user

    def update(self, user_id: int, user_data: dict) -> Optional[User]:
        """
        Update a user.

        Args:
            user_id: User ID
            user_data: Dictionary containing updated user data

        Returns:
            Updated user object if found, None otherwise
        """
        user = self.get_by_id(user_id)
        if not user:
            return None

        for key, value in user_data.items():
            if hasattr(user, key):
                setattr(user, key, value)

        self.db.commit()
        self.db.refresh(user)
        return user

    def delete(self, user_id: int) -> bool:
        """
        Delete a user (soft delete by setting is_active to False).

        Args:
            user_id: User ID

        Returns:
            True if deleted, False if not found
        """
        user = self.get_by_id(user_id)
        if not user:
            return False

        user.is_active = False
        self.db.commit()
        return True

    def get_active_users(self, company_id: Optional[int] = None) -> List[User]:
        """
        Get all active users, optionally filtered by company.

        Args:
            company_id: Optional company ID to filter by

        Returns:
            List of active users
        """
        query = self.db.query(User).filter(User.is_active == True)
        if company_id:
            query = query.filter(User.company_id == company_id)
        return query.all()

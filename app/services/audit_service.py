"""
Audit logging service.
"""

from typing import Optional, Dict, List, Any
from datetime import datetime
from sqlalchemy.orm import Session
from app.repositories.audit_repository import AuditRepository


class AuditService:
    """Service for audit logging."""

    def __init__(self, db: Session):
        self.db = db
        self.audit_repo = AuditRepository(db)

    def log_action(
        self,
        user_id: Optional[int],
        entity_type: str,
        entity_id: int,
        action: str,
        old_values: Optional[Dict[str, Any]] = None,
        new_values: Optional[Dict[str, Any]] = None,
        ip_address: Optional[str] = None,
    ) -> None:
        """
        Log an action to the audit trail.

        Args:
            user_id: ID of user performing the action (None for system actions)
            entity_type: Type of entity being modified
            entity_id: ID of the entity
            action: Action being performed
            old_values: Previous values (for updates)
            new_values: New values (for creates/updates)
            ip_address: IP address of the request
        """
        audit_data = {
            "user_id": user_id,
            "entity_type": entity_type,
            "entity_id": entity_id,
            "action": action,
            "old_values": old_values,
            "new_values": new_values,
            "ip_address": ip_address,
        }

        self.audit_repo.create(audit_data)

    def log_login(self, user_id: int, ip_address: Optional[str] = None) -> None:
        """
        Log a user login.

        Args:
            user_id: ID of user logging in
            ip_address: IP address of the request
        """
        self.log_action(
            user_id=user_id,
            entity_type="user",
            entity_id=user_id,
            action="login",
            ip_address=ip_address,
        )

    def log_logout(self, user_id: int, ip_address: Optional[str] = None) -> None:
        """
        Log a user logout.

        Args:
            user_id: ID of user logging out
            ip_address: IP address of the request
        """
        self.log_action(
            user_id=user_id,
            entity_type="user",
            entity_id=user_id,
            action="logout",
            ip_address=ip_address,
        )

    def get_entity_history(
        self, entity_type: str, entity_id: int, limit: int = 100
    ) -> List:
        """
        Get audit history for an entity.

        Args:
            entity_type: Type of entity
            entity_id: ID of entity
            limit: Maximum records to return

        Returns:
            List of audit log entries
        """
        return self.audit_repo.get_by_entity(entity_type, entity_id, limit)

    def get_user_activity(self, user_id: int, limit: int = 100) -> List:
        """
        Get activity history for a user.

        Args:
            user_id: User ID
            limit: Maximum records to return

        Returns:
            List of audit log entries
        """
        return self.audit_repo.get_by_user(user_id, limit)

    def get_recent_activity(
        self, days: int = 7, entity_type: Optional[str] = None, limit: int = 100
    ) -> List:
        """
        Get recent activity across the system.

        Args:
            days: Number of days to look back
            entity_type: Optional entity type filter
            limit: Maximum records to return

        Returns:
            List of recent audit log entries
        """
        return self.audit_repo.get_recent(days, entity_type, limit)

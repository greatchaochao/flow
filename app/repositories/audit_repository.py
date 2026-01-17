"""
Audit log repository for database operations.
"""

from typing import Optional, List
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import desc
from app.database.models import AuditLog


class AuditRepository:
    """Repository for audit log database operations."""

    def __init__(self, db: Session):
        self.db = db

    def create(self, audit_data: dict) -> AuditLog:
        """
        Create a new audit log entry.

        Args:
            audit_data: Dictionary containing audit log data

        Returns:
            Created audit log object
        """
        audit_log = AuditLog(**audit_data)
        self.db.add(audit_log)
        self.db.commit()
        self.db.refresh(audit_log)
        return audit_log

    def get_by_entity(
        self, entity_type: str, entity_id: int, limit: int = 100
    ) -> List[AuditLog]:
        """
        Get audit logs for a specific entity.

        Args:
            entity_type: Type of entity (e.g., 'payment', 'beneficiary')
            entity_id: Entity ID
            limit: Maximum number of records to return

        Returns:
            List of audit log entries
        """
        return (
            self.db.query(AuditLog)
            .filter(
                AuditLog.entity_type == entity_type, AuditLog.entity_id == entity_id
            )
            .order_by(desc(AuditLog.created_at))
            .limit(limit)
            .all()
        )

    def get_by_user(self, user_id: int, limit: int = 100) -> List[AuditLog]:
        """
        Get audit logs for a specific user.

        Args:
            user_id: User ID
            limit: Maximum number of records to return

        Returns:
            List of audit log entries
        """
        return (
            self.db.query(AuditLog)
            .filter(AuditLog.user_id == user_id)
            .order_by(desc(AuditLog.created_at))
            .limit(limit)
            .all()
        )

    def get_recent(
        self, days: int = 7, entity_type: Optional[str] = None, limit: int = 100
    ) -> List[AuditLog]:
        """
        Get recent audit logs.

        Args:
            days: Number of days to look back
            entity_type: Optional entity type filter
            limit: Maximum number of records to return

        Returns:
            List of recent audit log entries
        """
        cutoff_date = datetime.utcnow() - timedelta(days=days)
        query = self.db.query(AuditLog).filter(AuditLog.created_at >= cutoff_date)

        if entity_type:
            query = query.filter(AuditLog.entity_type == entity_type)

        return query.order_by(desc(AuditLog.created_at)).limit(limit).all()

    def get_by_action(
        self, action: str, entity_type: Optional[str] = None, limit: int = 100
    ) -> List[AuditLog]:
        """
        Get audit logs by action type.

        Args:
            action: Action type (e.g., 'created', 'updated', 'deleted')
            entity_type: Optional entity type filter
            limit: Maximum number of records to return

        Returns:
            List of audit log entries
        """
        query = self.db.query(AuditLog).filter(AuditLog.action == action)

        if entity_type:
            query = query.filter(AuditLog.entity_type == entity_type)

        return query.order_by(desc(AuditLog.created_at)).limit(limit).all()

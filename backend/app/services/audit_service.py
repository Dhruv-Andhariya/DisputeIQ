import uuid
from datetime import datetime
from typing import List, Dict, Any
from app.models.domain import AuditEvent
from app.database.db import save_audit_event, get_audit_events_by_dispute_id

class AuditService:
    @staticmethod
    def log_event(
        dispute_id: str,
        event_type: str,
        description: str,
        metadata: Dict[str, Any] = None
    ) -> AuditEvent:
        """Logs a persistent audit event into the database."""
        event = AuditEvent(
            event_id=f"AUD-{uuid.uuid4().hex[:8].upper()}",
            dispute_id=dispute_id,
            event_type=event_type,
            description=description,
            metadata=metadata or {},
            timestamp=datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        )
        save_audit_event(event)
        return event

    @staticmethod
    def get_audit_trail(dispute_id: str) -> List[AuditEvent]:
        """Retrieves chronological audit events for a dispute."""
        return get_audit_events_by_dispute_id(dispute_id)

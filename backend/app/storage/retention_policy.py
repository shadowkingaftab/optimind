"""Retention policy.

Converts the configured retention windows into concrete expiry timestamps
used by background cleanup jobs. Values are configuration inputs
(jurisdiction/compliance dependent).
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import timedelta

from app.utils.datetime import utcnow


@dataclass(frozen=True)
class RetentionPolicy:
    uploads_days: int = 30
    predictions_days: int = 365
    audit_logs_days: int = 730
    temporary_files_hours: int = 24
    quarantine_days: int = 7
    uploads_auto_delete: bool = True
    quarantine_auto_delete: bool = True

    def upload_cutoff(self):
        return utcnow() - timedelta(days=self.uploads_days)

    def temporary_cutoff(self):
        return utcnow() - timedelta(hours=self.temporary_files_hours)

    def quarantine_cutoff(self):
        return utcnow() - timedelta(days=self.quarantine_days)

    def audit_cutoff(self):
        return utcnow() - timedelta(days=self.audit_logs_days)

"""Password hashing and policy enforcement.

Hashing itself lives in :mod:`app.core.security`; this module re-exports the
safe wrappers and adds policy validation. Policy defaults mirror
``configs/security/password-policy.yaml`` and are deployment inputs.
"""

from __future__ import annotations

import re
from dataclasses import dataclass

from app.core.security import (
    hash_password,
    needs_rehash,
    verify_password,
)
from app.exceptions.validation import RequestValidationError

_UPPER = re.compile(r"[A-Z]")
_LOWER = re.compile(r"[a-z]")
_DIGIT = re.compile(r"[0-9]")
_SPECIAL = re.compile(r"[^A-Za-z0-9]")


@dataclass(frozen=True)
class PasswordPolicy:
    """Password complexity requirements.

    INPUT_REQUIRED: approve policy values per deployment. Defaults follow the
    repository configuration template and are not a compliance guarantee.
    """

    min_length: int = 12
    require_uppercase: bool = True
    require_lowercase: bool = True
    require_numbers: bool = True
    require_special_chars: bool = True
    max_length: int = 128


DEFAULT_PASSWORD_POLICY = PasswordPolicy()


def validate_password(
    password: str, policy: PasswordPolicy = DEFAULT_PASSWORD_POLICY
) -> None:
    """Validate ``password`` against ``policy``.

    Raises:
        RequestValidationError: listing the unmet requirements (no echo of the
            password itself).
    """
    problems: list[str] = []
    if len(password) < policy.min_length:
        problems.append(f"Password must be at least {policy.min_length} characters.")
    if len(password) > policy.max_length:
        problems.append(f"Password must be at most {policy.max_length} characters.")
    if policy.require_uppercase and not _UPPER.search(password):
        problems.append("Password must contain an uppercase letter.")
    if policy.require_lowercase and not _LOWER.search(password):
        problems.append("Password must contain a lowercase letter.")
    if policy.require_numbers and not _DIGIT.search(password):
        problems.append("Password must contain a number.")
    if policy.require_special_chars and not _SPECIAL.search(password):
        problems.append("Password must contain a special character.")
    if problems:
        raise RequestValidationError(
            "The password does not meet the required policy.",
            details={"requirements": problems},
        )


__all__ = [
    "DEFAULT_PASSWORD_POLICY",
    "PasswordPolicy",
    "hash_password",
    "needs_rehash",
    "validate_password",
    "verify_password",
]

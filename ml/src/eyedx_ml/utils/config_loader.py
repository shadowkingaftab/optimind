"""Configuration loading with explicit failure.

Loads YAML configs, resolves ``${ENV_VAR}`` placeholders, and validates that
required keys are present. Missing required configuration raises immediately so
pipelines never run on silently-defaulted clinical parameters.
"""

from __future__ import annotations

import os
import re
from pathlib import Path
from typing import Any, Dict, Mapping, Optional, Union

import yaml

__all__ = ["ConfigError", "load_yaml", "load_config", "resolve_env", "require_keys"]

_ENV_PATTERN = re.compile(r"\$\{([A-Za-z_][A-Za-z0-9_]*)\}")


class ConfigError(ValueError):
    """Raised when configuration is missing, malformed or unresolved."""


def _resolve_value(value: Any) -> Any:
    if isinstance(value, str):
        return resolve_env(value)
    if isinstance(value, dict):
        return {k: _resolve_value(v) for k, v in value.items()}
    if isinstance(value, list):
        return [_resolve_value(v) for v in value]
    return value


def resolve_env(value: str, *, strict: bool = False) -> str:
    """Replace ``${VAR}`` occurrences with environment values.

    With ``strict=True`` an unset variable raises :class:`ConfigError`; otherwise
    the placeholder is left intact so callers can detect it.
    """
    def _replace(match: re.Match[str]) -> str:
        name = match.group(1)
        env = os.environ.get(name)
        if env is None:
            if strict:
                raise ConfigError(f"environment variable not set: {name}")
            return match.group(0)
        return env

    return _ENV_PATTERN.sub(_replace, value)


def load_yaml(path: Union[str, Path]) -> Dict[str, Any]:
    """Load a YAML file into a dict (empty file -> empty dict)."""
    file_path = Path(path)
    if not file_path.is_file():
        raise ConfigError(f"config file not found: {file_path.name}")
    text = file_path.read_text(encoding="utf-8")
    if not text.strip():
        return {}
    data = yaml.safe_load(text)
    if data is None:
        return {}
    if not isinstance(data, dict):
        raise ConfigError(f"config root must be a mapping: {file_path.name}")
    return data


def load_config(
    path: Union[str, Path],
    *,
    required_keys: Optional[Mapping[str, Any]] = None,
    strict_env: bool = True,
) -> Dict[str, Any]:
    """Load YAML, resolve env placeholders and check required keys.

    ``required_keys`` is a nested mapping mirroring the config shape; every leaf
    key must be present in the loaded config.
    """
    data = _resolve_value(load_yaml(path))
    if required_keys:
        require_keys(data, required_keys, prefix="")
    return data


def require_keys(
    data: Mapping[str, Any],
    required: Mapping[str, Any],
    *,
    prefix: str = "",
) -> None:
    """Raise if any required key (recursively) is absent."""
    for key, sub in required.items():
        if key not in data:
            raise ConfigError(f"missing required config key: {prefix}{key}")
        if isinstance(sub, Mapping):
            child = data[key]
            if not isinstance(child, Mapping):
                raise ConfigError(f"expected mapping at: {prefix}{key}")
            require_keys(child, sub, prefix=f"{prefix}{key}.")

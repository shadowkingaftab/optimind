"""Demographic statistics with small-cell suppression.

Aggregates counts over coarse, non-identifying metadata columns (for example an
age bucket or site) and suppresses any cell below ``min_cell_size`` so the
report cannot be used to re-identify individuals. Only columns that are not
direct identifiers should be requested.
"""

from __future__ import annotations

from collections import Counter
from dataclasses import dataclass, field
from typing import Dict, List, Mapping, Optional, Sequence

from eyedx_ml.data.ingestion.metadata_importer import MetadataTable

__all__ = ["DemographicStatistics", "compute_demographic_statistics"]

_NON_IDENTIFYING_HINT = ("bucket", "site", "device", "sex", "gender", "eye")


@dataclass
class DemographicStatistics:
    min_cell_size: int = 5
    suppressed_cells: int = 0
    tables: Dict[str, Dict[str, Dict[str, int]]] = field(default_factory=dict)

    def as_dict(self) -> dict:
        return {
            "min_cell_size": self.min_cell_size,
            "suppressed_cells": self.suppressed_cells,
            "tables": self.tables,
        }


def _is_safe_column(column: str, requested: Sequence[str]) -> bool:
    lowered = column.lower()
    if any(token in lowered for token in ("name", "mrn", "id_number", "dob")):
        return False
    return column in requested or any(h in lowered for h in _NON_IDENTIFYING_HINT)


def compute_demographic_statistics(
    tables: Mapping[str, MetadataTable],
    *,
    columns: Optional[Mapping[str, Sequence[str]]] = None,
    min_cell_size: int = 5,
) -> DemographicStatistics:
    """Compute per-column value counts with small-cell suppression.

    ``columns`` optionally restricts which columns are aggregated per table.
    """
    stats = DemographicStatistics(min_cell_size=min_cell_size)

    for table_name, table in tables.items():
        requested = list((columns or {}).get(table_name, ()))
        aggregated: Dict[str, Dict[str, int]] = {}
        for column in table.columns:
            if column.endswith("_key") or column == "record_id":
                continue
            if columns is not None:
                allowed = column in requested
            else:
                allowed = _is_safe_column(column, requested)
            if not allowed:
                continue
            counter: Counter = Counter()
            for row in table.rows:
                value = (row.get(column) or "").strip() or "unknown"
                counter[value] += 1
            cells: Dict[str, int] = {}
            for value, count in sorted(counter.items()):
                if count < min_cell_size:
                    stats.suppressed_cells += 1
                    cells[value] = -1
                else:
                    cells[value] = count
            if cells:
                aggregated[column] = cells
        if aggregated:
            stats.tables[table_name] = aggregated
    return stats

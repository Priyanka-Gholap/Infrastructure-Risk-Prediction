"""
Project Service Module for SIH26103.

Manages in-memory caching, indexing, lookup, and search for the
current inference dataset (current_inference_dataset.csv) produced in Step 6B.
"""

import logging
from pathlib import Path
from typing import Any
import pandas as pd

from backend.app.config import settings
from backend.app.schemas import ProjectLookupItem

logger = logging.getLogger("sih26103.project_service")


class ProjectNotFoundError(Exception):
    """Raised when a requested project_id does not exist in the current inference dataset."""

    def __init__(self, project_id: str):
        self.project_id = project_id
        super().__init__(f"Project '{project_id}' was not found in the current inference dataset.")


class DatasetUnavailableError(Exception):
    """Raised when the current inference dataset is missing, unreadable, or invalid."""


class ProjectService:
    def __init__(self, dataset_path: Path | None = None):
        self.dataset_path: Path = dataset_path or settings.CURRENT_INFERENCE_DATASET_PATH
        self._df: pd.DataFrame | None = None
        self._project_records: dict[str, dict[str, Any]] = {}
        self._metadata_list: list[ProjectLookupItem] = []
        self._is_loaded: bool = False

    @property
    def is_loaded(self) -> bool:
        return self._is_loaded

    def load_dataset(self, override_path: Path | None = None) -> None:
        """
        Loads current_inference_dataset.csv into memory once, parses records,
        and constructs an in-memory index for O(1) project lookup and deterministic search.
        """
        target_path = override_path or self.dataset_path
        logger.info("Loading current inference dataset from: %s", target_path)

        if not target_path.exists():
            # Check fallback in reports/
            fallback_path = settings.PROJECT_ROOT / "reports" / "current_inference_dataset.csv"
            if fallback_path.exists():
                logger.info("Primary path not found. Loading fallback dataset from: %s", fallback_path)
                target_path = fallback_path
            else:
                logger.error("Current inference dataset file does not exist: %s", target_path)
                raise DatasetUnavailableError("Current inference dataset file is not available on server.")

        try:
            df = pd.read_csv(target_path, dtype={"project_id": str})
        except Exception as exc:
            logger.error("Failed to parse current inference dataset CSV: %s", exc)
            raise DatasetUnavailableError(f"Failed to parse current inference dataset: {exc}") from exc

        # Validate required lookup metadata columns
        required_cols = {"project_id", "project_name", "snapshot_month"}
        missing_cols = required_cols - set(df.columns)
        if missing_cols:
            raise DatasetUnavailableError(f"Current inference dataset is missing required metadata columns: {missing_cols}")

        self._df = df
        self._project_records = {}
        self._metadata_list = []

        # Sort deterministically by project_id ascending
        df_sorted = df.sort_values("project_id").copy()

        for _, row in df_sorted.iterrows():
            pid = str(row["project_id"]).strip()
            pname = str(row["project_name"]) if pd.notna(row["project_name"]) else ""
            smonth = str(row["snapshot_month"]) if pd.notna(row["snapshot_month"]) else ""

            # Store in-memory lookup record
            self._project_records[pid] = row.to_dict()

            # Store lightweight lookup item
            self._metadata_list.append(
                ProjectLookupItem(
                    project_id=pid,
                    project_name=pname,
                    snapshot_month=smonth,
                )
            )

        self._is_loaded = True
        logger.info("Loaded %d current project snapshots successfully.", len(self._project_records))

    def get_project(self, project_id: str) -> dict[str, Any]:
        """
        Retrieves the complete snapshot record for a project.
        Raises ProjectNotFoundError if not present.
        """
        if not self._is_loaded:
            self.load_dataset()

        clean_pid = str(project_id).strip()
        if clean_pid not in self._project_records:
            logger.warning("Project lookup failed: '%s' not found", clean_pid)
            raise ProjectNotFoundError(clean_pid)

        return self._project_records[clean_pid]

    def search_projects(
        self,
        search: str | None = None,
        limit: int = 50,
        offset: int = 0,
    ) -> list[ProjectLookupItem]:
        """
        Searches currently monitored projects by project_id or project_name
        (case-insensitive substring match), ordered deterministically by project_id.
        Applies limit and offset for pagination.
        """
        if not self._is_loaded:
            self.load_dataset()

        candidates = self._metadata_list

        if search and search.strip():
            query = search.strip().lower()
            candidates = [
                item for item in candidates
                if query in item.project_id.lower() or query in item.project_name.lower()
            ]

        # Apply offset and limit
        return candidates[offset: offset + limit]


# Singleton instance
_project_service_instance: ProjectService | None = None


def get_project_service() -> ProjectService:
    global _project_service_instance
    if _project_service_instance is None:
        _project_service_instance = ProjectService()
    return _project_service_instance

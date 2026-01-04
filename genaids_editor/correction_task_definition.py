"""Tâche de correction textuelle."""
from __future__ import annotations

from enum import Enum
from typing import Any, Dict, List, Optional

from pydantic import field_validator

from genaids_editor.config import config

from genaids_editor.core.models.tasks_definition.base_task_definition import (
    AcceptedInputFormat,
    BaseTaskDefinition,
    InputDocumentCardinality,
)


class CorrectionLevel(str, Enum):
    """Niveaux de correction disponibles."""

    ORTHOGRAPH = "orthograph"
    SYNTAX = "syntax"
    REFORMULATION = "reformulation"
    COMBINED = "combined"  # Syntax + Reformulation


def _get_allowed_correction_levels() -> List[CorrectionLevel]:
    """
    Retourne niveaux autorisés selon is_genai_enabled().

    Logic:
        - is_genai_enabled()=False : ORTHOGRAPH uniquement (ML local)
        - is_genai_enabled()=True  : Tous niveaux (LLM)
    """
    if not config.is_genai_enabled():
        return [CorrectionLevel.ORTHOGRAPH]
    return [
        CorrectionLevel.ORTHOGRAPH,
        CorrectionLevel.SYNTAX,
        CorrectionLevel.REFORMULATION,
        CorrectionLevel.COMBINED,
    ]

# Alias conservé pour compatibilité (patch/tests)
is_genai_enabled = config.is_genai_enabled


class CorrectionTaskDefinition(BaseTaskDefinition):
    """Tâche de correction textuelle."""

    levels: List[CorrectionLevel] = [CorrectionLevel.ORTHOGRAPH]
    ignore_protected_runs: bool = True

    # Cardinalité documentaire
    supported_input_type: InputDocumentCardinality = InputDocumentCardinality.SINGLE

    # ✅ Formats acceptés
    accepted_formats: List[AcceptedInputFormat] = [AcceptedInputFormat.DOCX]

    @field_validator("levels")
    @classmethod
    def validate_levels(cls, v: List[CorrectionLevel]) -> List[CorrectionLevel]:
        """Validate correction levels."""
        if not v:
            raise ValueError("At least one correction level is required")
        # Conserver l'ordre et les doublons (tests vérifient la longueur exacte)
        return v

    @field_validator("glossary")
    @classmethod
    def validate_glossary(cls, v: Optional[Dict[str, str]]) -> Optional[Dict[str, str]]:
        """Validate glossary format."""
        if v is None:
            return None

        if not isinstance(v, dict):
            raise ValueError(f"glossary must be dict, got {type(v)}")

        if not all(isinstance(k, str) and isinstance(val, str) for k, val in v.items()):
            raise ValueError("glossary must be dict[str, str] (term -> definition)")

        if not v:
            raise ValueError("glossary cannot be empty dict (use None instead)")

        return v

    def validate_task(self) -> None:
        """Validate correction task."""
        if not self.levels:
            raise ValueError("At least one correction level is required")

        is_genai = config.is_genai_enabled()
        allowed_levels = _get_allowed_correction_levels()
        invalid_levels = [lvl for lvl in self.levels if lvl not in allowed_levels]

        if invalid_levels:
            allowed_names = [lvl.value for lvl in allowed_levels]
            invalid_names = [lvl.value for lvl in invalid_levels]
            raise ValueError(
                f"Correction levels {invalid_names} not supported "
                f"(is_genai_enabled()={is_genai}). "
                f"Allowed: {allowed_names}"
            )

    def to_execution_config(self) -> Dict[str, Any]:
        """Convertit en config exécution."""
        return {
            "task_type": "correction",
            "levels": [lvl.value for lvl in self.levels],
            "ignore_protected_runs": self.ignore_protected_runs,
            "glossary": self.glossary or {},
            "sections": self.sections.model_dump() if self.sections else None,
        }

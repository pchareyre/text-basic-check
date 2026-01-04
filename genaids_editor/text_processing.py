"""
Input/Output data types for text processing.
"""
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional


class TaskStatus(str, Enum):
    """Status des tâches de traitement."""

    PENDING = "pending"
    DONE = "done"
    WARNING = "warning"
    ERROR = "error"


@dataclass
class TextProcessingUnit:
    """
    Unité de traitement texte individuelle.

    Représente un segment de texte à traiter (paragraphe, phrase, etc.).

    Attributes:
        text_id: Identifiant unique
        text: Texte à traiter
        actions: Liste actions demandées (ex: ["spelling"])
        task_status: Statut traitement (pending/done/warning/error)
        msg: Message optionnel (erreurs, warnings)
        metadata: Métadonnées additionnelles (stats, etc.)

    Examples:
        >>> unit = TextProcessingUnit(
        ...     text_id="p1",
        ...     text="This is a teste",
        ...     actions=["spelling"]
        ... )
    """

    text_id: str
    text: str
    actions: List[str] = field(default_factory=list)
    task_status: TaskStatus = TaskStatus.PENDING
    msg: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        """Normalisation actions (lowercase)."""
        self.actions = [action.lower() for action in self.actions]

    def is_valid(self) -> bool:
        """Valide structure (text_id et actions présents)."""
        return bool(self.text_id and self.actions)

    def has_action(self, action: str) -> bool:
        """Vérifie si action demandée."""
        return action.lower() in self.actions

    def mark_done(self, corrected_text: str, **metadata_updates: Any) -> "TextProcessingUnit":
        """Marque unité comme traitée avec succès."""
        return TextProcessingUnit(
            text_id=self.text_id,
            text=corrected_text,
            actions=self.actions,
            task_status=TaskStatus.DONE,
            msg=None,
            metadata={**self.metadata, **metadata_updates},
        )

    def mark_warning(
        self, text: str, message: str, **metadata_updates: Any
    ) -> "TextProcessingUnit":
        """Marque unité avec warning."""
        return TextProcessingUnit(
            text_id=self.text_id,
            text=text,
            actions=self.actions,
            task_status=TaskStatus.WARNING,
            msg=message,
            metadata={**self.metadata, **metadata_updates},
        )

    def mark_error(self, error_message: str) -> "TextProcessingUnit":
        """Marque unité en erreur."""
        return TextProcessingUnit(
            text_id=self.text_id,
            text=self.text,
            actions=self.actions,
            task_status=TaskStatus.ERROR,
            msg=error_message,
            metadata=self.metadata,
        )


@dataclass
class TextProcessingBatch:
    """
    Batch de traitement texte avec métadonnées globales.

    Conteneur pour plusieurs TextProcessingUnit avec configuration partagée
    (glossaire, custom_words, langue, etc.).

    Attributes:
        units: Liste des unités de texte à traiter
        metadata: Métadonnées globales appliquées à toutes les unités
            - glossary: Dict[term, replacement] - Glossaire global
                * Si term == replacement → préservation
                * Si term ≠ replacement → remplacement automatique
            - custom_words: List[str] - Mots personnalisés à préserver
            - language: str - Langue forcée ("English"/"French", optionnel)
            - detect_language: bool - Auto-détection langue (défaut: True)
            - ...autres métadonnées personnalisées...

    Examples:
        >>> # Batch avec glossaire
        >>> batch = TextProcessingBatch(
        ...     units=[
        ...         TextProcessingUnit(text_id="p1", text="ML is great", actions=["spelling"]),
        ...         TextProcessingUnit(text_id="p2", text="AI is powerful", actions=["spelling"]),
        ...     ],
        ...     metadata={
        ...         "glossary": {"ML": "Machine Learning", "AI": "Artificial Intelligence"},
        ...         "custom_words": ["GenAIDS"],
        ...         "language": "English"
        ...     }
        ... )

        >>> # Batch simple
        >>> batch = TextProcessingBatch(
        ...     units=[...],
        ...     metadata={"detect_language": True}
        ... )
    """

    units: List[TextProcessingUnit] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        """Validation et valeurs par défaut."""
        # Valeurs par défaut metadata
        if "detect_language" not in self.metadata:
            self.metadata["detect_language"] = True

        if "language" not in self.metadata:
            self.metadata["language"] = "English"

    @property
    def glossary(self) -> Optional[Dict[str, str]]:
        """Récupère glossaire global."""
        return self.metadata.get("glossary")

    @property
    def custom_words(self) -> Optional[List[str]]:
        """Récupère custom_words globaux."""
        return self.metadata.get("custom_words")

    @property
    def language(self) -> str:
        """Récupère langue configurée."""
        return str(self.metadata.get("language", "English"))

    @property
    def detect_language(self) -> bool:
        """Récupère mode détection langue."""
        return bool(self.metadata.get("detect_language", True))

    def add_unit(self, unit: TextProcessingUnit) -> None:
        """Ajoute une unité au batch."""
        self.units.append(unit)

    def add_units(self, units: List[TextProcessingUnit]) -> None:
        """Ajoute plusieurs unités au batch."""
        self.units.extend(units)

    def get_valid_units(self) -> List[TextProcessingUnit]:
        """Retourne unités valides."""
        return [unit for unit in self.units if unit.is_valid()]

    def get_units_by_action(self, action: str) -> List[TextProcessingUnit]:
        """Retourne unités avec action spécifique."""
        return [unit for unit in self.units if unit.has_action(action)]

    def count_by_status(self) -> Dict[TaskStatus, int]:
        """Compte unités par statut."""
        counts = {status: 0 for status in TaskStatus}
        for unit in self.units:
            counts[unit.task_status] += 1
        return counts

    def has_warnings(self) -> bool:
        """Vérifie si batch contient warnings."""
        return any(unit.task_status == TaskStatus.WARNING for unit in self.units)

    def has_errors(self) -> bool:
        """Vérifie si batch contient erreurs."""
        return any(unit.task_status == TaskStatus.ERROR for unit in self.units)

    def to_dict(self) -> Dict[str, Any]:
        """Sérialise batch en dictionnaire."""
        return {
            "units": [
                {
                    "text_id": unit.text_id,
                    "text": unit.text,
                    "actions": unit.actions,
                    "task_status": unit.task_status.value,
                    "msg": unit.msg,
                    "metadata": unit.metadata,
                }
                for unit in self.units
            ],
            "metadata": self.metadata,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "TextProcessingBatch":
        """Crée batch depuis dictionnaire."""
        units = [
            TextProcessingUnit(
                text_id=u["text_id"],
                text=u["text"],
                actions=u["actions"],
                task_status=TaskStatus(u["task_status"]),
                msg=u.get("msg"),
                metadata=u.get("metadata", {}),
            )
            for u in data["units"]
        ]

        return cls(units=units, metadata=data.get("metadata", {}))

    def to_segments_dict(
        self, corrected_only: bool = False, only_done: bool = False, log_health: bool = True
    ) -> Dict[str, str]:
        """
        Extract segments as dictionary with flexible filtering.

        Unified extraction method supporting multiple use cases:
        - Document reconstruction: All valid segments (corrected_only=False)
        - Update application: Only modified segments (corrected_only=True)

        Filtering Logic:
            - DONE status → unit.text (corrected if modified, otherwise unchanged)
            - !=DONE status (ERROR/WARNING) → original_text from metadata (if only_done=False)

        Args:
            corrected_only: If True, return only metadata["corrected"]=True segments
            only_done: If True, skip !=DONE statuses; if False, include with original_text
            log_health: If True, log batch health statistics (default: True)

        Returns:
            Dict {text_id: text} where text is:
            - unit.text if DONE (and passes corrected_only filter)
            - original_text if !=DONE and only_done=False (fallback recovery)

        Examples:
            >>> # All valid segments (document reconstruction)
            >>> batch.to_segments_dict(corrected_only=False)
            >>> # {"p0": "corrected", "p1": "unchanged", "p2": "unchanged"}

            >>> # Only corrected segments (update application)
            >>> batch.to_segments_dict(corrected_only=True)
            >>> # {"p0": "corrected"}

            >>> # Include error recovery
            >>> batch.to_segments_dict(corrected_only=False, only_done=False)
            >>> # {"p0": "corrected", "p1": "unchanged", "p2": "original_fallback"}
        """
        segments = {}

        for unit in self.units:
            # Filter by status
            if unit.task_status == TaskStatus.DONE:
                # Filter by corrected flag if requested
                if corrected_only and not unit.metadata.get("corrected", False):
                    continue

                segments[unit.text_id] = unit.text

            # Include !=DONE with original_text if only_done=False
            elif not only_done:
                original = unit.metadata.get("original_text", unit.text)
                segments[unit.text_id] = original

        # Optional health logging
        if log_health:
            try:
                from genaids_editor.utils.correction.segment_health_from_batch import (
                    log_batch_health,
                )

                log_batch_health(self, segments, log_unprocessed_details=True)
            except ImportError as e:
                # Fallback: Import failed, log basic stats without health utility
                import logging

                logger = logging.getLogger(__name__)
                logger.warning(
                    f"[to_segments_dict] ⚠️ segment_health_from_batch import failed: {e}"
                )
                logger.info(
                    f"[to_segments_dict] 📊 Returning {len(segments)}/{len(self.units)} segments"
                )

        return segments

    def to_updates_dict(self, log_health: bool = True) -> Dict[str, str]:
        """
        Convert batch to updates dictionary - ONLY corrected texts.

        Convenient shortcut for to_segments_dict(corrected_only=True, only_done=True).

        Purpose:
            Extract texts that were actually modified by correctors.
            Use for document updates where only changed segments matter.

        Args:
            log_health: If True, log batch health statistics (default: True)

        Returns:
            Dictionary mapping text_id to corrected text
            Only includes units with metadata["corrected"] = True

        Examples:
            >>> batch = TextProcessingBatch(units=[...])
            >>> updates = batch.to_updates_dict()
            >>> # {"p0": "corrected text", "p1": "another correction"}
        """
        return self.to_segments_dict(corrected_only=True, only_done=True, log_health=log_health)

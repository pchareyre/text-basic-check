"""Base task definition - Common structure for all editing tasks."""
from abc import ABC, abstractmethod
from enum import Enum
from typing import Any, Dict, List, Literal, Optional, Union

from pydantic import BaseModel, field_validator


class InputDocumentCardinality(str, Enum):
    """Cardinalité documentaire de la tâche : document unique ou multiples."""

    SINGLE = "single"  # Single-document operation
    MULTI = "multi"  # Multi-document operation (comparison, diff, etc.)


class AcceptedInputFormat(str, Enum):
    """Formats de document supportés."""

    DOCX = "docx"
    XLSX = "xlsx"
    PPTX = "pptx"
    PDF = "pdf"
    ALL_OOXML = "all_ooxml"  # docx, xlsx, pptx
    ALL = "all"  # Tous formats


class SectionTarget(BaseModel):
    """
    Section targeting options (format-agnostic).

    Supports:
    - Universal values: "all", "document_only"
    - Format-specific: ["slides", "notes"] (PPTX), ["sheet1", "sheet2"] (XLSX)

    Examples:
        >>> # All sections (universal)
        >>> target = SectionTarget.all()

        >>> # Document body only (DOCX/PPTX/XLSX compatible)
        >>> target = SectionTarget.document_only()

        >>> # PPTX-specific: slides + notes
        >>> target = SectionTarget(parts=["slides", "notes"])

        >>> # XLSX-specific: specific sheets
        >>> target = SectionTarget(parts=["sheet1", "sheet2"])

        >>> # DOCX-specific: body + headers
        >>> target = SectionTarget(parts=["document", "headers"])
    """

    parts: Union[str, List[str]]  # "all" | "document_only" | ["document", "headers", ...]
    exclude: Optional[List[str]] = None
    slide_range: Optional[List[int]] = None  # PPTX helper
    sheet_names: Optional[List[str]] = None  # XLSX helper
    cell_ranges: Optional[Dict[str, str]] = None  # XLSX helper

    @classmethod
    def all(cls) -> "SectionTarget":
        """All sections (universal)."""
        return cls(parts="all")

    @classmethod
    def document_only(cls) -> "SectionTarget":
        """Main document content only (no headers/footers/notes)."""
        return cls(parts="document_only")

    @classmethod
    def custom(cls, parts: List[str]) -> "SectionTarget":
        """Custom section list (format-specific)."""
        return cls(parts=parts)

    @classmethod
    def slides(cls, slide_range: Optional[List[int]] = None) -> "SectionTarget":
        """PPTX slides selector with optional range."""
        return cls(parts=["slide"], slide_range=slide_range)

    @classmethod
    def sheets(
        cls,
        sheet_names: Optional[List[str]] = None,
        cell_ranges: Optional[Dict[str, str]] = None,
    ) -> "SectionTarget":
        """XLSX sheet selector with optional ranges."""
        base_parts: Union[str, List[str]] = sheet_names if sheet_names else "sheet"
        return cls(parts=base_parts, sheet_names=sheet_names, cell_ranges=cell_ranges)

    def is_all(self) -> bool:
        """Check if all sections targeted."""
        return self.parts == "all"

    def is_document_only(self) -> bool:
        """Check if document body only."""
        return self.parts == "document_only"

    def has_part(self, part: str) -> bool:
        """Check if specific part is targeted."""
        if part is None:
            return False

        if isinstance(self.parts, str):
            return self.parts == "all" or self.parts == part
        return part in self.parts

    def to_section_filter(self, format_type: str) -> Dict[str, Any]:
        """Convert SectionTarget to editor-friendly filter dict."""
        fmt = format_type.lower()

        def _ensure_list(val: Union[str, List[str]]) -> List[str]:
            return [val] if isinstance(val, str) else list(val)

        if fmt == "docx":
            if self.parts == "all":
                include = ["document", "header", "footer", "footnote", "endnote"]
            elif self.parts == "document_only":
                include = ["document"]
            else:
                include = _ensure_list(self.parts)
        elif fmt == "pptx":
            include = ["slide", "notes"] if self.parts == "all" else _ensure_list(self.parts)
        elif fmt == "xlsx":
            base = ["sheet"] if self.parts == "all" else _ensure_list(self.parts)
            if self.sheet_names:
                base.extend(self.sheet_names)
            include = base
        else:
            include = _ensure_list(self.parts)

        if self.exclude:
            include = [p for p in include if p not in self.exclude]

        # Deduplicate while preserving order
        seen = set()
        include_types = []
        for item in include:
            if item not in seen:
                include_types.append(item)
                seen.add(item)

        filter_dict: Dict[str, Any] = {"include_types": include_types}

        if fmt == "pptx" and self.slide_range:
            filter_dict["slide_range"] = self.slide_range

        if fmt == "xlsx" and self.cell_ranges:
            filter_dict["cell_ranges"] = self.cell_ranges

        return filter_dict


"""Edit mode enumeration - Defines how text corrections are applied."""


class EditMode(str, Enum):
    """
    Edit mode for text corrections.

    Values:
        DIRECT: Apply corrections directly (replace text in-place)
            - Fast, no revision history
            - Use for automated/trusted corrections
            - Compatible: DOCX, GDOC, XLSX, PPTX

        TRACK_CHANGES: Apply corrections with track changes markup
            - Creates revision suggestions (user review)
            - Preserves original + shows changes
            - Compatible: DOCX (w:ins/w:del), GDOC (suggestions API)
            - Fallback to DIRECT for XLSX/PPTX (no track changes support)

    Examples:
        >>> from genaids_editor.core.models.tasks_definition import EditMode
        >>> task = CorrectionTaskDefinition(
        ...     correction_types=["ORTHOGRAPHY"],
        ...     edit_mode=EditMode.TRACK_CHANGES  # ← User review mode
        ... )

        >>> # Direct replacement (no review)
        >>> task = CorrectionTaskDefinition(
        ...     correction_types=["ORTHOGRAPHY"],
        ...     edit_mode=EditMode.DIRECT
        ... )
    """

    DIRECT = "direct"
    """Direct text replacement (no revision markup)."""

    TRACK_CHANGES = "track_changes"
    """Track changes markup (user review mode)."""

    def supports_format(self, format_type: str) -> bool:
        """
        Check if edit mode is supported for a format.

        Args:
            format_type: Document format ("DOCX", "GDOC", "XLSX", "PPTX")

        Returns:
            bool: True if supported, False otherwise

        Examples:
            >>> EditMode.TRACK_CHANGES.supports_format("DOCX")
            True
            >>> EditMode.TRACK_CHANGES.supports_format("XLSX")
            False  # XLSX has no track changes
        """
        if self == EditMode.DIRECT:
            return True  # Direct always supported

        if self == EditMode.TRACK_CHANGES:
            # Track changes supported for DOCX and GDOC
            return format_type.upper() in ["DOCX", "GDOC"]

        return False

    def get_fallback_for_format(self, format_type: str) -> "EditMode":
        """
        Get fallback mode if not supported for format.

        Args:
            format_type: Document format

        Returns:
            EditMode: Original mode if supported, else DIRECT

        Examples:
            >>> EditMode.TRACK_CHANGES.get_fallback_for_format("XLSX")
            EditMode.DIRECT  # XLSX doesn't support track changes
        """
        if self.supports_format(format_type):
            return self
        return EditMode.DIRECT


class BaseTaskDefinition(BaseModel, ABC):
    """Base class for all task definitions."""

    edit_mode: EditMode = EditMode.DIRECT
    sections: Optional[SectionTarget] = None
    glossary: Optional[Dict[str, str]] = None
    ignore_protected: bool = True

    # Cardinalité documentaire (single/multi)
    supported_input_type: InputDocumentCardinality = InputDocumentCardinality.SINGLE

    # ✅ NOUVEAU: Formats acceptés
    accepted_formats: List[AcceptedInputFormat] = [AcceptedInputFormat.DOCX]

    @field_validator("sections")
    @classmethod
    def validate_sections(cls, v: Optional[SectionTarget]) -> Optional[SectionTarget]:
        """Validate section target value."""
        if v is None:
            return None

        # Basic validation
        if isinstance(v.parts, str):
            if v.parts not in ["all", "document_only"]:
                raise ValueError(
                    f"Invalid section target string: {v.parts}. "
                    f"Valid: 'all', 'document_only', or list of parts"
                )
        elif isinstance(v.parts, list):
            if not v.parts:
                raise ValueError("Section parts list cannot be empty")

        return v

    @field_validator("edit_mode")
    @classmethod
    def validate_edit_mode(cls, v: EditMode) -> EditMode:
        """
        Validate edit mode value.

        Note:
            Format-specific validation happens in workflow
            (e.g., fallback TRACK_CHANGES → DIRECT for XLSX)
        """
        if not isinstance(v, EditMode):
            raise ValueError(f"edit_mode must be EditMode enum, got {type(v)}")
        return v

    def validate_input_type(self, is_multi_source: bool) -> None:
        """Valide compatibilité cardinalité documentaire (single/multi)."""
        if is_multi_source:
            if self.supported_input_type != InputDocumentCardinality.MULTI:
                raise ValueError(
                    f"{type(self).__name__} does not support multi-source input. "
                    f"Multi-source requires tuple: (doc1, doc2, ...). "
                    f"Use batch for multiple documents: [doc1, doc2, doc3]"
                )
        else:
            if self.supported_input_type != InputDocumentCardinality.SINGLE:
                raise ValueError(
                    f"{type(self).__name__} requires multi-source input. "
                    f"Provide tuple of documents: (doc1, doc2, ...)"
                )

    def validate_format_compatibility(self, detected_format: str) -> None:
        """
        Valide compatibilité format document / tâche.

        Args:
            detected_format: Format détecté ("docx", "xlsx", "pptx", etc.)

        Raises:
            ValueError: Si format non supporté par la tâche

        Examples:
            >>> task = CorrectionTaskDefinition()
            >>> task.validate_format_compatibility("docx")  # ✅ OK
            >>> task.validate_format_compatibility("xlsx")  # ❌ ValueError
        """
        # Résolution formats acceptés
        accepted = set()
        for fmt in self.accepted_formats:
            if fmt == AcceptedInputFormat.ALL:
                accepted.update(["docx", "xlsx", "pptx", "pdf"])
            elif fmt == AcceptedInputFormat.ALL_OOXML:
                accepted.update(["docx", "xlsx", "pptx"])
            else:
                accepted.add(fmt.value)

        # Validation
        if detected_format not in accepted:
            accepted_str = ", ".join(sorted(accepted))
            raise ValueError(
                f"{type(self).__name__} does not support format '{detected_format}'. "
                f"Accepted formats: {accepted_str}"
            )

    @abstractmethod
    def validate_task(self) -> None:
        """Validate task configuration (implemented by subclasses)."""
        pass

    def to_dict(self) -> Dict[str, Any]:
        """Export task as dictionary."""
        return self.model_dump(exclude_none=True)

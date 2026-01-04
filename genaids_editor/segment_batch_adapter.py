"""
Segment ↔ TextProcessingBatch adapter.

Bidirectional conversion for text processing pipeline:
- segments_to_batch(): Segment[] → TextProcessingBatch
- batch_to_valid_segments(): TextProcessingBatch → Dict[text_id, text] (all valid segments)

Design principles:
    - Segment = Local document snapshot (lxml references, runs, formatting)
    - TextProcessingUnit = Work order (detached, text-only)
    - TextProcessingBatch = Container + global metadata (glossary, custom_words)

Usage:
    >>> from genaids_editor.core.adapters.segment_batch_adapter import (
    ...     segments_to_batch,
    ...     batch_to_valid_seg
    ... )
    >>> 
    >>> # Convert segments to batch
    >>> batch = segments_to_batch(
    ...     segments=editor.segments,
    ...     actions=["spelling"],
    ...     glossary={"ML": "Machine Learning"}
    ... )
    >>> 
    >>> # Apply corrector
    >>> corrector = BasicTextChecker()
    >>> result_batch = corrector.correct_batch(batch)
    >>> 
    >>> # Extract valid_seg
    >>> valid_seg = batch_to_valid_segments(result_batch)
"""
from typing import Any, Dict, List, Optional

from genaids_editor.text_segment import Segment
from genaids_editor.text_processing import TextProcessingBatch, TextProcessingUnit


def segments_to_batch(
    segments: List[Segment],
    actions: Optional[List[str]] = None,
    glossary: Optional[Dict[str, str]] = None,
    custom_words: Optional[List[str]] = None,
    detect_language: bool = True,
    language: str = "English",
    skip_empty: bool = False,  # ✅ NOUVEAU paramètre
    **extra_metadata: Any,
) -> TextProcessingBatch:
    """
    Convert Segment[] → TextProcessingBatch.
    - Segment metadata preserved in unit.metadata
    
    Filtering:
        - if requested : Empty segments skipped (no text or whitespace only)
        

    Args:
        segments: Document segments (local snapshot with lxml references)
        actions: Actions requested (default: ["spelling"])
        glossary: Global glossary {term: replacement}
            - If term == replacement → preserve word
            - If term ≠ replacement → auto-replace
        custom_words: Custom words to preserve (brand names, etc.)
        detect_language: Enable language auto-detection
        language: Fallback language if detect_language=False
        skip_empty: Skip empty segments (default: False)
        **extra_metadata: Additional batch metadata

    Returns:
        TextProcessingBatch ready for processing

    Examples:
        >>> # Simple conversion
        >>> batch = segments_to_batch(
        ...     segments=editor.segments,
        ...     actions=["spelling"]
        ... )

        >>> # With glossary
        >>> batch = segments_to_batch(
        ...     segments=editor.segments,
        ...     actions=["spelling"],
        ...     glossary={"ML": "Machine Learning"},
        ...     custom_words=["Capgemini"]
        ... )
    """
    # Default actions
    if actions is None:
        actions = ["spelling"]

    units = []

    for seg in segments:
        # ✅ Filtrage optionnel
        if skip_empty and (not seg.text or not seg.text.strip()):
            continue

        # ✅ Convert Segment → TextProcessingUnit
        unit = TextProcessingUnit(
            text_id=seg.text_id,
            text=seg.text,
            actions=actions,
            metadata={
                # ✅ Preserve segment-specific metadata (traceability)
                "segment_type": seg.type,
                "section_type": seg.metadata.get("section_type"),
                "has_protected_runs": bool(seg.protected_runs),
                "original_text": seg.text,  # ← Store original for change detection
                "original_segment_metadata": seg.metadata.copy(),
            },
        )

        units.append(unit)

    # ✅ Build TextProcessingBatch with global metadata
    batch = TextProcessingBatch(
        units=units,
        metadata={
            "glossary": glossary or {},
            "custom_words": custom_words or [],
            "detect_language": detect_language,
            "language": language,
            **extra_metadata,
        },
    )

    return batch


def batch_to_valid_segments(batch: TextProcessingBatch, only_done: bool = True) -> Dict[str, str]:
    """
    Convert TextProcessingBatch → Dict[text_id, text] extracting all valid segments.

    Adapter façade providing stable interface to batch.to_segments_dict().

    Concept: "Valid text" vs "Corrected text"
        - Valid text = Text exploitable for document reconstruction (always usable)
        - Corrected text = Text modified by corrector (subset of valid, flagged with corrected=True)

    Extraction Logic:
        - DONE status → unit.text (corrected if modified, otherwise unchanged input)
        - !=DONE status (ERROR/WARNING) → original_text from metadata (error recovery fallback)
        
    Rejection Guarantee:
        Never returns error messages like "erreur - dog n'est pas un mot connu en francais"
        → Always returns actual text content (processed or original)

    Purpose:
        - Document reconstruction: No missing segments, all text_ids present
        - Treatment chaining: Pass all valid texts to next corrector stage
        - Fault tolerance: Processing errors don't break document structure

    Args:
        batch: Processed batch (after corrector applied)
        only_done: If True, include only DONE units; if False, include all statuses (default: True)

    Returns:
        Dict {text_id: text} where text is:
        - unit.text if DONE (corrected or unchanged, both are valid)
        - original_text if !=DONE (error recovery, prevents data loss)
        
    Note:
        Different from to_updates_dict() which filters metadata["corrected"]=True only.
        This returns ALL DONE segments with valid text for document reconstruction.

    Examples:
        >>> result_batch = corrector.correct_batch(batch)
        >>> segments = batch_to_valid_segments(result_batch)
        >>> # {"p0": "Les chats corrected", "p1": "unchanged input", "p2": "original (ERROR fallback)"}
    """
    # Delegate to unified method in batch
    valid_seg = batch.to_segments_dict(corrected_only=False, only_done=only_done, log_health=False)

    # Use centralized health logging with adapter context
    from genaids_editor.segment_health_from_batch import log_batch_health
    log_batch_health(
        batch,
        valid_seg,
        caller_name="batch_to_valid_segments",
        log_unprocessed_details=True
    )

    return valid_seg

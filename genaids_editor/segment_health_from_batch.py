"""
Batch health monitoring utility.

Provides logging and statistics for TextProcessingBatch processing results.
Automatically detects caller context for meaningful log messages.
"""
import inspect
import logging
from typing import Any, Dict, Optional

from genaids_editor.text_processing import TaskStatus, TextProcessingBatch

# Use root logger to ensure visibility with any logging configuration
logger = logging.getLogger(__name__)


def log_batch_health(
    batch: TextProcessingBatch,
    result_dict: Dict[str, str],
    caller_name: Optional[str] = None,
    log_unprocessed_details: bool = False,
) -> Dict[str, Any]:
    """
    Log batch processing health with detailed breakdown.

    Automatically detects caller context and logs statistics at INFO level.
    Optionally logs unprocessed segment details at DEBUG level.

    Args:
        batch: Processed batch to analyze
        result_dict: Resulting dictionary from extraction (for count validation)
        caller_name: Override caller name (auto-detected if None)
        log_unprocessed_details: If True, log DEBUG details for unprocessed units

    Returns:
        Dict with statistics:
        {
            "total": int,
            "returned": int,
            "corrected": int,
            "unchanged": int,
            "errors": int,
            "warnings": int,
            "reverted": int
        }

    Examples:
        >>> result = batch.to_segments_dict(corrected_only=False)
        >>> stats = log_batch_health(batch, result)
        >>> # [to_segments_dict] 📊 Returning 45 entries: 12 corrected, 30 unchanged, 3 reverted
    """
    # Auto-detect caller if not provided
    if caller_name is None:
        frame = inspect.currentframe()
        if frame and frame.f_back:
            caller_name = frame.f_back.f_code.co_name
        else:
            caller_name = "unknown"

    # Calculate statistics
    corrected_count = sum(
        1
        for unit in batch.units
        if unit.task_status == TaskStatus.DONE and unit.metadata.get("corrected", False)
    )
    unchanged_count = sum(
        1
        for unit in batch.units
        if unit.task_status == TaskStatus.DONE and not unit.metadata.get("corrected", False)
    )
    error_count = sum(1 for unit in batch.units if unit.task_status == TaskStatus.ERROR)
    warning_count = sum(1 for unit in batch.units if unit.task_status == TaskStatus.WARNING)

    # Reverted = ERROR + WARNING (units that failed processing)
    reverted_count = error_count + warning_count

    # Build stats dict
    stats = {
        "total": len(batch.units),
        "returned": len(result_dict),
        "corrected": corrected_count,
        "unchanged": unchanged_count,
        "errors": error_count,
        "warnings": warning_count,
        "reverted": reverted_count,
    }

    # INFO: Summary log with caller context
    logger.info(
        f"[{caller_name}] 📊 Returning {len(result_dict)}/{len(batch.units)} entries: "
        f"{corrected_count} corrected, {unchanged_count} unchanged, {reverted_count} ERROR/WARNING(s)  "
    )

    # DEBUG: Detailed breakdown of unprocessed units
    if log_unprocessed_details and (error_count > 0 or warning_count > 0):
        logger.debug(f"[{caller_name}] 🔍 Unprocessed units breakdown:")

        if error_count > 0:
            logger.debug(f"  ❌ {error_count} ERROR(s):")
            for unit in batch.units:
                if unit.task_status == TaskStatus.ERROR:
                    logger.debug(f"    - {unit.text_id}: {unit.msg or 'No message'}")
                    logger.debug(f"      Text preview: {unit.text[:80]}...")

        if warning_count > 0:
            logger.debug(f"  ⚠️  {warning_count} WARNING(s):")
            for unit in batch.units:
                if unit.task_status == TaskStatus.WARNING:
                    logger.debug(f"    - {unit.text_id}: {unit.msg or 'No message'}")
                    logger.debug(f"      Text preview: {unit.text[:80]}...")

    return stats


def get_batch_stats(batch: TextProcessingBatch) -> Dict[str, Any]:
    """
    Get batch statistics without logging.

    Quick stats extraction for programmatic use.

    Args:
        batch: Batch to analyze

    Returns:
        Dict with counts by status and correction state

    Examples:
        >>> stats = get_batch_stats(batch)
        >>> print(f"Corrected: {stats['corrected']}/{stats['total']}")
    """
    stats = {
        "total": len(batch.units),
        "done": 0,
        "corrected": 0,
        "unchanged": 0,
        "errors": 0,
        "warnings": 0,
        "pending": 0,
    }

    for unit in batch.units:
        if unit.task_status == TaskStatus.DONE:
            stats["done"] += 1
            if unit.metadata.get("corrected", False):
                stats["corrected"] += 1
            else:
                stats["unchanged"] += 1
        elif unit.task_status == TaskStatus.ERROR:
            stats["errors"] += 1
        elif unit.task_status == TaskStatus.WARNING:
            stats["warnings"] += 1
        elif unit.task_status == TaskStatus.PENDING:
            stats["pending"] += 1

    return stats

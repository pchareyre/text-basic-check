"""
Corrector Protocol - Standard interface for all correctors.

All correctors (adapters or utils) must follow this interface to be compatible
with the correction workflow.

Interface Contract:
    - Input: TextProcessingBatch
    - Output: TextProcessingBatch (modified in-place)
    - Post-conditions: metadata["corrected"] flag set for each unit

Implementations:
    - SpellCheckerAdapter (orthographic_check wrapper)
    - RandomCorrector (test mock)
    - GenAIAdapter (future)
    - TranslatorAdapter (future)

Usage:
    >>> from genaids_editor.core.adapters import CorrectorProtocol
    >>> 
    >>> def workflow(corrector: CorrectorProtocol):
    ...     result = corrector.correct_batch(batch)
    >>> 
    >>> workflow(SpellCheckerAdapter())  # ✅ Type-checked by IDE
"""
from typing import Protocol, runtime_checkable

from genaids_editor.text_processing import TextProcessingBatch


@runtime_checkable
class CorrectorProtocol(Protocol):
    """
    Protocol for all corrector implementations.

    All correctors must implement:
        correct_batch(batch: TextProcessingBatch) -> TextProcessingBatch

    Post-conditions (REQUIRED for each unit):
        1. metadata["corrected"] = True   (if text was modified)
        2. metadata["corrected"] = False  (if text unchanged)
        3. task_status = TaskStatus.DONE  (if processed successfully)
        4. task_status = TaskStatus.ERROR (if processing failed)

    Optional metadata (for debugging):
        - metadata["original_text"]: Text before correction
        - metadata["corrected_words"]: List of corrected words
        - metadata["error_message"]: Error details if task_status=ERROR

    Examples:
        >>> # Implementing a custom corrector
        >>> class MyCorrector:
        ...     def correct_batch(self, batch: TextProcessingBatch) -> TextProcessingBatch:
        ...         for unit in batch.units:
        ...             # Apply correction logic
        ...             if unit.text != modified_text:
        ...                 unit.text = modified_text
        ...                 unit.metadata["corrected"] = True
        ...             else:
        ...                 unit.metadata["corrected"] = False
        ...             unit.task_status = TaskStatus.DONE
        ...         return batch
        >>>
        >>> # Using Protocol for type hints
        >>> def run_workflow(corrector: CorrectorProtocol):
        ...     batch = segments_to_batch(segments)
        ...     result = corrector.correct_batch(batch)
        ...     corrections = batch_to_valid_segments(result)
        ...     return corrections
        >>>
        >>> # Works with any corrector following protocol
        >>> run_workflow(SpellCheckerAdapter())
        >>> run_workflow(RandomCorrector())
        >>> run_workflow(MyCorrector())

    Type Checking:
        >>> isinstance(SpellCheckerAdapter(), CorrectorProtocol)  # True (runtime)
        >>> # mypy/pyright will validate at static analysis time
    """

    def correct_batch(self, batch: TextProcessingBatch) -> TextProcessingBatch:
        """
        Apply corrections to batch.

        Args:
            batch: Input batch with units to correct
                - batch.units: List of TextProcessingUnit
                - batch.metadata: Dict with glossary, custom_words, etc.

        Returns:
            Corrected batch (same object, modified in-place)

        Post-conditions (MUST be enforced):
            For each unit in batch.units:
                - unit.metadata["corrected"] = True/False (REQUIRED)
                - unit.task_status = DONE or ERROR (REQUIRED)
                - unit.text may be modified (if corrected=True)

        Raises:
            RuntimeError: If correction fails (should set task_status=ERROR instead)

        Notes:
            - Batch is modified in-place (efficient)
            - Original text should be preserved in metadata["original_text"]
            - Empty/whitespace-only text should set corrected=False
        """
        ...


def validate_corrector_output(batch: TextProcessingBatch) -> None:
    """
    Validate corrector output follows protocol.

    Checks:
        - All units have metadata["corrected"] flag
        - All units have valid task_status

    Args:
        batch: Batch returned by corrector

    Raises:
        ValueError: If protocol violated

    Usage:
        >>> result_batch = corrector.correct_batch(batch)
        >>> validate_corrector_output(result_batch)  # Raises if invalid
    """
    from genaids_editor.text_processing import TaskStatus

    for unit in batch.units:
        # Check "corrected" flag exists
        if "corrected" not in unit.metadata:
            raise ValueError(
                f"Unit {unit.text_id} missing required metadata['corrected'] flag. "
                f"Corrector must set corrected=True/False for all units."
            )

        # Check flag is boolean
        if not isinstance(unit.metadata["corrected"], bool):
            raise ValueError(
                f"Unit {unit.text_id} has invalid corrected flag: {unit.metadata['corrected']}. "
                f"Must be bool (True/False)."
            )

        # Check task_status is valid
        if unit.task_status not in [TaskStatus.DONE, TaskStatus.ERROR, TaskStatus.WARNING]:
            raise ValueError(
                f"Unit {unit.text_id} has invalid task_status: {unit.task_status}. "
                f"Must be DONE, ERROR, or WARNING."
            )

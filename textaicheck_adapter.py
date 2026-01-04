"""TextAICheck Adapter - Wrapper around textaicheck.AdvancedTextChecker for LLM-based corrections."""
import logging
from typing import Dict, List, Optional

from genaids_editor.core.models.tasks_definition.correction_task_definition import CorrectionLevel
from genaids_editor.core.models.text_segment import Segment
from genaids_editor.orthographic_check import TaskStatus, TextProcessingBatch

from genaids_editor.utils.logging_config import setup_logger

logger = setup_logger(__name__)

logger = logging.getLogger(__name__)


class TextAICheckAdapter:
    """
    Adapter for textaicheck library to perform LLM-based text corrections.

    Wraps textaicheck.AdvancedTextChecker to provide syntax correction, reformulation,
    and translation capabilities using LLM endpoints.

    Follows CorrectorProtocol interface for seamless integration with genaids-editor workflows.

    Examples:
        >>> from genaids_editor.core.adapters import TextAICheckAdapter
        >>>
        >>> adapter = TextAICheckAdapter(language="English", verbose=True)
        >>> batch = TextProcessingBatch(...)
        >>> corrected_batch = adapter.correct_batch(batch)
    """

    def __init__(
        self,
        language: str = "English",
        verbose: bool = False,
        use_optimizer: bool = False,
        optimizer_config: Optional[Dict] = None,
        **llm_kwargs,
    ):
        """
        Initialize TextAICheckAdapter.

        Args:
            language: Target language for corrections/translations (default: "English")
            verbose: Enable detailed logging
            use_optimizer: Enable BatchProcessingOptimizer for performance
            optimizer_config: Optimizer configuration:
                - enable_cache: Enable LRU cache (default: True)
                - enable_parallel: Enable parallel processing (default: True)
                - enable_dedup: Enable deduplication (default: True)
                - enable_prefilter: Enable pre-filtering (default: False)
                - max_batch_size: Max units per batch (default: 20)
                - cache_maxsize: Max cache entries (default: 1000)
                - cache_ttl: Cache TTL in seconds (default: 3600)
            **llm_kwargs: Optional LLM configuration parameters:
                - model_name: LLM model to use
                - temperature: LLM temperature setting
                - gen_eng_openai_api_url: OpenAI API endpoint URL
                - max_completion_tokens: Maximum completion tokens
                - max_tokens_allowed: Maximum tokens per request
                - prompt_task_message: Custom prompt message
        """
        self.language = language
        self.verbose = verbose
        self.llm_kwargs = llm_kwargs
        self.use_optimizer = use_optimizer

        # Lazy initialization - only import when needed
        self._checker = None
        
        # Initialize optimizer if requested
        self.optimizer: Optional[BatchProcessingOptimizer]
        if self.use_optimizer:
            from genaids_editor.core.adapters.batch_processing_optimizer import (
                BatchProcessingOptimizer,
            )
            
            optimizer_config = optimizer_config or {}
            self.optimizer = BatchProcessingOptimizer(
                verbose=verbose,
                **optimizer_config,
            )
        else:
            self.optimizer = None

    @property
    def checker(self):
        """Lazy-load AdvancedTextChecker to avoid import errors if textaicheck not installed."""
        if self._checker is None:
            try:
                from textaicheck.text_checkers import AdvancedTextChecker

                self._checker = AdvancedTextChecker(language=self.language, **self.llm_kwargs)
            except ImportError as e:
                raise ImportError(
                    "textaicheck library not found. " "Please install it: poetry add textaicheck"
                ) from e
        return self._checker

    def correct_batch(self, batch: TextProcessingBatch) -> TextProcessingBatch:
        """
        Apply LLM-based corrections to batch.

        Implements CorrectorProtocol interface.

        Args:
            batch: Input batch with units to correct
                - batch.units: List of TextProcessingUnit
                - batch.metadata: Dict with glossary, custom_words, etc.

        Returns:
            Corrected batch (modified in-place)

        Post-conditions:
            For each unit in batch.units:
                - unit.metadata["corrected"] = True/False
                - unit.task_status = DONE or ERROR
                - unit.text modified if corrected=True

        Note:
            Uses textaicheck.AdvancedTextChecker for LLM-based corrections.
            Supports syntax correction, reformulation, and translation.
            
            If use_optimizer=True, applies performance optimizations:
            - Cache, deduplication, parallel processing, etc.
        """
        if self.verbose:
            logger.debug(f"[TextAICheckAdapter] Processing {len(batch.units)} units")
            logger.debug(f"  - language: {self.language}")
            logger.debug(f"  - glossary: {len(batch.glossary or {})} terms")
            logger.debug(f"  - optimizer: {self.use_optimizer}")

        # Delegate to optimizer if enabled
        if self.optimizer:
            corrected_batch = self.optimizer.optimize(
                batch=batch,
                process_callback=self._internal_correct,
                cache_key_context={"glossary": batch.metadata.get("glossary")},
            )
        else:
            # Direct processing without optimizations
            corrected_batch = self._internal_correct(batch)

        # Always finalize metadata (adapter responsibility)
        self._finalize_batch_metadata(corrected_batch)

        return corrected_batch

    def _internal_correct(self, batch: TextProcessingBatch) -> TextProcessingBatch:
        """
        Internal correction logic - can be called by optimizer or directly.
        
        Args:
            batch: Batch to process
            
        Returns:
            Batch with corrections applied (without finalization)
        """
        # Convert batch to textaicheck format
        textaicheck_input = self._batch_to_textaicheck_format(batch)

        if not textaicheck_input:
            if self.verbose:
                logger.debug("[TextAICheckAdapter] No units to process")
            return batch

        try:
            # Call textaicheck.AdvancedTextChecker
            if self.verbose:
                logger.debug(
                    f"[TextAICheckAdapter] Calling LLM for {len(textaicheck_input)} entries..."
                )

            corrections = self.checker.correct(textaicheck_input)

            # Apply corrections back to batch (without finalization)
            self._apply_corrections_to_batch(batch, corrections)

            if self.verbose:
                corrected_count = sum(
                    1 for unit in batch.units if unit.metadata.get("corrected", False)
                )
                logger.debug(
                    f"[TextAICheckAdapter] Corrected {corrected_count}/{len(batch.units)} units"
                )

        except Exception as e:
            logger.error(f"TextAICheckAdapter failed: {e}")

            # Mark all units as ERROR
            for unit in batch.units:
                unit.task_status = TaskStatus.ERROR
                unit.msg = f"LLM correction failed: {str(e)}"
                unit.metadata["corrected"] = False

            if self.verbose:
                logger.debug(f"[TextAICheckAdapter] ERROR: {e}")

        return batch

    def _batch_to_textaicheck_format(self, batch: TextProcessingBatch) -> List[Dict]:
        """
        Convert TextProcessingBatch to textaicheck input format.

        Args:
            batch: genaids-editor batch

        Returns:
            List of InputTextEntry dicts for textaicheck

        Format:
            [
                {
                    "text": "...",
                    "text_id": "...",
                    "correction_type": ["syntax", "reformulation"]
                }
            ]
        """
        from textaicheck.input_output_data_types import InputTextEntry

        textaicheck_input = []

        for unit in batch.units:
            # Determine correction_type from unit.actions
            correction_types = self._map_actions_to_correction_types(unit.actions)

            if not correction_types:
                # Skip units with no recognized actions
                continue

            entry: InputTextEntry = {
                "text": unit.text,
                "text_id": unit.text_id,
                "correction_type": correction_types,
            }

            textaicheck_input.append(entry)

        return textaicheck_input

    def _map_actions_to_correction_types(self, actions: List[str]) -> List[str]:
        """
        Map genaids-editor actions to textaicheck correction_type.

        Args:
            actions: List of actions from TextProcessingUnit (e.g., ["syntax", "reformulation"])

        Returns:
            List of correction_type strings for textaicheck

        Valid textaicheck correction_type values (LLM-based only):
            - "syntax" - Grammar/syntax correction (LLM)
            - "reformulation" - Style/reformulation (LLM)
            - "translation" - Translation (LLM)

        NOT SUPPORTED:
            - "orthography" - NOT processed by textaicheck LLM (use SpellCheckerAdapter)

        Note:
            TextAICheck AdvancedTextChecker.correct() only processes:
            - syntax corrections via LLM
            - reformulation via LLM
            Orthography entries are filtered out and ignored by process_json().
        """
        correction_types = []

        for action in actions:
            action_lower = action.lower()

            # Only accept LLM-supported types
            if action_lower in ["syntax", "reformulation", "translation"]:
                if action_lower not in correction_types:
                    correction_types.append(action_lower)

            # Warn about unsupported types
            elif action_lower == "orthography":
                if self.verbose:
                    logger.debug(
                        f"[TextAICheckAdapter] WARNING: orthography not supported by textaicheck LLM"
                    )

            # Legacy mappings (skip orthography-related)
            elif action_lower in ["grammar"]:
                if "syntax" not in correction_types:
                    correction_types.append("syntax")

            elif action_lower in ["style", "rephrase"]:
                if "reformulation" not in correction_types:
                    correction_types.append("reformulation")

        return correction_types

    def _apply_corrections_to_batch(self, batch: TextProcessingBatch, corrections: List):
        """
        Apply textaicheck corrections back to batch.

        Args:
            batch: Original batch (modified in-place)
            corrections: List of OutputChangedResult from textaicheck

        Note:
            OutputChangedResult is a Pydantic model with attributes:
            - text_id: str
            - modified_text: str
        """
        # Create lookup dict for fast access
        # Handle both Pydantic models and dicts
        corrections_dict = {}
        for corr in corrections:
            if hasattr(corr, "text_id"):
                # Pydantic model
                corrections_dict[corr.text_id] = corr.modified_text
            else:
                # Dict (fallback)
                corrections_dict[corr["text_id"]] = corr["modified_text"]

        # Apply to each unit
        changed_count = 0
        unchanged_count = 0
        
        for unit in batch.units:
            if unit.text_id in corrections_dict:
                corrected_text = corrections_dict[unit.text_id]

                # ✅ Compare with CURRENT text (unit.text), not original
                # This handles batch chaining: unit.text may already be modified by previous corrector
                
                # DEBUG: Log first few comparisons
                if changed_count + unchanged_count < 3:
                    logger.debug(f"[_apply_corrections] {unit.text_id[:20]}...")
                    logger.debug(f"  current (input): {unit.text[:50]}...")
                    logger.debug(f"  corrected (output): {corrected_text[:50]}...")
                    logger.debug(f"  changed? {corrected_text != unit.text}")
                
                if corrected_text != unit.text:
                    # Apply correction - text was modified by THIS corrector
                    unit.text = corrected_text
                    unit.metadata["corrected"] = True
                    unit.task_status = TaskStatus.DONE
                    changed_count += 1
                else:
                    # No change by THIS corrector - keep current text (don't revert!)
                    # unit.text stays as-is (may already be modified by previous step)
                    unit.metadata["corrected"] = False
                    unit.task_status = TaskStatus.DONE
                    unchanged_count += 1
            else:
                # Not in corrections (should not happen)
                # Keep current text (don't modify unit.text)
                unit.metadata["corrected"] = False
                unit.task_status = TaskStatus.DONE
                unchanged_count += 1
        
        if self.verbose:
            logger.debug(f"[_apply_corrections] {changed_count} changed, {unchanged_count} unchanged")

    def _finalize_batch_metadata(self, batch: TextProcessingBatch) -> None:
        """
        Finalize metadata flags for all units after processing.
        
        Sets consistent metadata based on text comparison with original:
        - unit.metadata["corrected"] = True if text changed from original
        - unit.metadata["original_text"] preserved (set by segments_to_batch)
        - unit.task_status = DONE
        
        Called by:
        - Base adapter: after _apply_corrections_to_batch()
        - Optimized adapter: after _merge_all_results()
        
        Note: Idempotent - safe to call multiple times
        """
        corrected_count = 0
        unchanged_count = 0
        error_count = 0
        
        for unit in batch.units:
            # Get original text from metadata (set by segments_to_batch)
            original_text = unit.metadata.get("original_text")
            
            if original_text is None:
                # No original stored - assume unchanged
                if "corrected" not in unit.metadata:
                    unit.metadata["corrected"] = False
                if unit.task_status != TaskStatus.ERROR:
                    unit.task_status = TaskStatus.DONE
                    unchanged_count += 1
                else:
                    error_count += 1
                    
            elif unit.text != original_text:
                # Text changed - mark as corrected
                unit.metadata["corrected"] = True
                unit.task_status = TaskStatus.DONE
                corrected_count += 1
                # original_text already in metadata
                
            else:
                # Text unchanged
                unit.metadata["corrected"] = False
                unit.task_status = TaskStatus.DONE
                unchanged_count += 1
        
        # INFO LOG - Always visible
        logger.info(f"[_finalize_batch_metadata] Total {len(batch.units)} units: {corrected_count} corrected, {unchanged_count} unchanged, {error_count} errors")


def correct_with_textaicheck(
    segments: List[Segment],
    levels: List[CorrectionLevel],
    glossary: Optional[Dict[str, str]] = None,
    verbose: bool = False,
) -> TextProcessingBatch:
    """
    Apply corrections using TextAICheckAdapter (textaicheck library).

    Convenience function for integration with correction_workflow.

    Args:
        segments: Segments to correct
        levels: Correction levels (SYNTAX, REFORMULATION - NOT ORTHOGRAPH)
        glossary: Glossary terms to preserve
        verbose: Enable detailed logging

    Returns:
        TextProcessingBatch: Corrected batch with metadata["corrected"] flags
            - unit.text contains corrected text (or original if unchanged)
            - unit.metadata["corrected"] = True/False
            - unit.metadata["original_text"] preserved

    Note:
        Uses textaicheck.AdvancedTextChecker for LLM-based corrections.
        ORTHOGRAPH level is NOT supported - filtered out automatically.
        Use simple_correct_orthography for orthography corrections.

        Supported correction types:
        - "syntax": Grammar and syntax corrections
        - "reformulation": Rewrite for clarity/style
        - Combined: Both syntax and reformulation together
        
        Benefits of returning batch (vs dict):
        - Preserves metadata (corrected flags, status, actions)
        - Enables batch chaining/composition
        - Consistent with adapter.correct_batch() output
    """
    from genaids_editor.core.adapters import segments_to_batch

    # Filter out ORTHOGRAPH - not supported by textaicheck
    actions = _levels_to_actions(levels)

    if verbose:
        logger.debug(f"[textaicheck_corrector] Processing {len(segments)} segments")
        logger.debug(f"[textaicheck_corrector] Actions: {actions}")

    # Convert segments to batch format
    batch = segments_to_batch(
        segments,
        actions=actions,
        glossary=glossary,
        custom_words=[],
        language="en",  # TODO: Make configurable
        detect_language=False,
    )

    if verbose:
        logger.debug(f"[textaicheck_corrector] Created batch with {len(batch.units)} units")

    # Create adapter with optimizer
    adapter = TextAICheckAdapter(
        language="English",
        verbose=verbose,
        use_optimizer=True,
        optimizer_config={
            "enable_cache": True,
            "enable_parallel": True,
            "enable_prefilter": False,  # Désactivé: trop agressif, skip trop de segments
            "enable_dedup": True,
            "max_batch_size": 20,
        },
    )

    try:
        corrected_batch = adapter.correct_batch(batch)

        if verbose:
            corrected_count = sum(1 for u in corrected_batch.units if u.metadata.get("corrected", False))
            logger.debug(f"[textaicheck_corrector] Returning batch: {corrected_count}/{len(corrected_batch.units)} corrected")

        return corrected_batch

    except Exception as e:
        if verbose:
            logger.debug(f"[textaicheck_corrector] ERROR: {e}")

        # Return batch with error status on all units
        for unit in batch.units:
            unit.task_status = TaskStatus.ERROR
            unit.msg = f"Correction failed: {str(e)}"
            unit.metadata["corrected"] = False
        
        return batch


def _levels_to_actions(levels: List[CorrectionLevel]) -> List[str]:
    """
    Convert CorrectionLevel to textaicheck correction_type strings.

    Args:
        levels: List of CorrectionLevel enums

    Returns:
        List of correction_type strings for InputTextEntry

    Mapping (to match textaicheck correction_type):
        - CorrectionLevel.ORTHOGRAPH → NOT SUPPORTED (use simple_correct_orthography instead)
        - CorrectionLevel.SYNTAX → ["syntax" , "orthograph"]
        - CorrectionLevel.REFORMULATION → ["reformulation", "syntax" , "orthograph"]
        - CorrectionLevel.COMBINED → ["syntax", "reformulation"]

    Note:
        TextAICheck does NOT handle orthography corrections.
        Orthography must be handled separately by simple_correct_orthography.
    """
    actions = []

    # Filter out ORTHOGRAPH - not supported by textaicheck
    filtered_levels = [l for l in levels if l != CorrectionLevel.ORTHOGRAPH]

    for level in filtered_levels:
        if level == CorrectionLevel.SYNTAX:
            actions.append("syntax")
        elif level == CorrectionLevel.REFORMULATION:
            actions.append("reformulation")
        elif level == CorrectionLevel.COMBINED:
            # Combined = syntax + reformulation
            if "syntax" not in actions:
                actions.append("syntax")
            if "reformulation" not in actions:
                actions.append("reformulation")

    return actions

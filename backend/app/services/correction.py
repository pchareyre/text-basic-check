"""
Text correction services.

Provides spell checking and grammar correction functionality.
"""

from text_basic_check import SpellChecker
from typing import Optional
from pathlib import Path

# Try to import T5 dependencies
try:
    from transformers import AutoTokenizer
    from optimum.onnxruntime import ORTModelForSeq2SeqLM
    T5_AVAILABLE = True
except ImportError:
    T5_AVAILABLE = False


class T5ModelService:
    """Service for managing T5 model."""
    
    _instance = None
    _model = None
    _tokenizer = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(T5ModelService, cls).__new__(cls)
        return cls._instance
    
    def load_model(self, model_dir: str = "t5-small-onnx-q"):
        """Load T5 ONNX model and tokenizer."""
        if not T5_AVAILABLE:
            raise RuntimeError("T5 dependencies not installed")
        
        if self._model is None or self._tokenizer is None:
            model_path = Path(model_dir)
            if not model_path.exists():
                raise RuntimeError(f"T5 model not found at {model_path}")
            
            self._tokenizer = AutoTokenizer.from_pretrained(
                model_dir,
                use_fast=True,
                local_files_only=True
            )
            
            self._model = ORTModelForSeq2SeqLM.from_pretrained(
                model_dir,
                file_name="encoder_model.onnx",
                decoder_file_name="decoder_model.onnx",
                decoder_with_past_file_name="decoder_with_past_model.onnx",
                local_files_only=True
            )
        
        return self._tokenizer, self._model
    
    @property
    def is_loaded(self) -> bool:
        """Check if model is loaded."""
        return self._model is not None and self._tokenizer is not None


class SpellCheckingService:
    """Service for spell checking using SymSpell."""
    
    def __init__(self, language: str = 'en'):
        self.checker = SpellChecker(language=language)
    
    def correct_text(self, text: str) -> str:
        """Apply SymSpell spell checking correction."""
        return self.checker.correct_text(text)
    
    def analyze(self, text: str) -> dict:
        """Analyze text and return error information."""
        return self.checker.analyze(text)


class GrammarCorrectionService:
    """Service for grammar correction using T5."""
    
    def __init__(self, model_dir: str = "t5-small-onnx-q"):
        self.model_dir = model_dir
        self.t5_service = T5ModelService()
    
    def is_available(self) -> bool:
        """Check if T5 is available."""
        return T5_AVAILABLE
    
    def correct_text(
        self,
        text: str,
        num_beams: int = 1,
        max_new_tokens: int = 64
    ) -> str:
        """Apply T5 grammar correction."""
        if not self.is_available():
            raise RuntimeError("T5 not available")
        
        tokenizer, model = self.t5_service.load_model(self.model_dir)
        
        # Prepend instruction for better correction
        input_text = f"grammar: {text}"
        
        inputs = tokenizer(input_text, return_tensors="pt")
        outputs = model.generate(
            **inputs,
            max_new_tokens=max_new_tokens,
            num_beams=num_beams,
            no_repeat_ngram_size=3,
            early_stopping=True
        )
        
        result = tokenizer.decode(outputs[0], skip_special_tokens=True)
        return result
    
    def correct_text_chunked(
        self,
        text: str,
        chunk_size: int = 500,
        num_beams: int = 1
    ) -> str:
        """Correct text in chunks for longer texts."""
        if len(text) <= chunk_size:
            return self.correct_text(text, num_beams=num_beams)
        
        # Split into sentences
        sentences = text.split('.')
        corrected_sentences = []
        
        for sentence in sentences:
            if sentence.strip():
                corrected = self.correct_text(
                    sentence.strip() + '.',
                    num_beams=num_beams
                )
                corrected_sentences.append(corrected)
        
        return ' '.join(corrected_sentences)

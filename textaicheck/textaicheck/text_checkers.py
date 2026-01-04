from .input_output_data_types import InputTextEntry, OutputChangedResult, OutputCompareResult, InputTextEntryMinimal
from typing import List, Optional
from .json_text_splitter import process_json
from .minify_json_to_pairs import minify_json
from .prompt_generator import generate_prompt
from langchain_openai import ChatOpenAI
import tiktoken
from .config_loader import load_config
import ast
from .apply_changes import apply_changes
import os
import logging
from dotenv import load_dotenv

class AdvancedTextChecker:
    """Class to perform correction/reformulation through LLM"""
    def __init__(self, language: str="English", **kwargs):
        """
        Initialize AdvancedTextChecker with optional settings.

        Args:
            language (str): Language of the input text. (default: "English")
            kwargs (dict): Optional arguments to initialize the object.
        """
        # Optional arguments for LLM call
        model_name = kwargs.get("model_name")
        default_model_encoding = kwargs.get("default_model_encoding")
        temperature = kwargs.get("temperature")
        generative_engine_openai_api_url = kwargs.get("gen_eng_openai_api_url")
        max_completion_tokens = kwargs.get("max_completion_tokens")

        # Optional argument for json chunking
        max_tokens_allowed = kwargs.get("max_tokens_allowed")

        # Optional argument for certain tasks, namely, translate
        self.language = language

        # Optional argument for prompt message
        self.prompt_task_message = kwargs.get("prompt_task_message")

        # read default config parameters if not provided as input
        config = load_config(config_purpose="llm")
        self.constants = config.get("constants")
        
        # ✨ OPTIMIZATION: Initialize caches early
        self._encoding_cache: Optional[tiktoken.Encoding] = None
        self._llm_cache: Optional[ChatOpenAI] = None
        
        if default_model_encoding is None:
            self.default_model_encoding = self.constants.get("DEFAULT_MODEL_ENCODING")
        if model_name is None:
            self.model_name = self.constants.get("MODEL_NAME")
            self.model_encoding = self._get_encoding_from_model()
        else:
            self.model_name = model_name
            self.model_encoding = self._get_encoding_from_model()
        if temperature is None:
            self.temperature = self.constants.get("TEMPERATURE")
        else:
            self.temperature = temperature
        if generative_engine_openai_api_url is None:
            self.generative_engine_openai_api_url = self.constants.get("GEN_ENG_OPENAI_API_URL")
        else:
            self.generative_engine_openai_api_url = generative_engine_openai_api_url
        if max_tokens_allowed is None:
            self.max_tokens_allowed = int(self.constants.get("MAX_TOKENS_ALLOWED"))
        else:
            self.max_tokens_allowed = max_tokens_allowed
        if max_completion_tokens is None:
            self.max_completion_tokens = self.constants.get("MAX_COMPLETION_TOKENS")
        else:
            self.max_completion_tokens = max_completion_tokens

    def _get_encoding_from_model(self):
        """Get encoding for OpenAI model (cached)."""
        if self._encoding_cache is not None:
            return self._encoding_cache
        
        try:
            self._encoding_cache = tiktoken.encoding_for_model(self.model_name)
            return self._encoding_cache
        except KeyError:
            print(f"Model {self.model_name} not found, using default {self.default_model_encoding}")
            self._encoding_cache = tiktoken.get_encoding("cl100k_base")
            return self._encoding_cache

    def correct(self, data: List[InputTextEntry]) -> List[OutputChangedResult]:
        """
        Correction: performs basic spell checking, syntax correction and reformulation when required
        in the input data.
        Args:
            data : List[InputTextEntry]
        Output
            correction_results: List[OutputCorrectedText]
        """
        spellcheck_text, syntaxcheck_text, reformulate_text = process_json(data, clean=True)

        # Apply syntax corrections:
        #   (1) transform data into minimal expression,
        #   (2) generate prompt
        #   (3) send to LLM or SLM
        minimal_data_syntax = minify_json(syntaxcheck_text)
        corrected_syntax = self._invoke_llm(minimal_data_syntax, task="syntax")

        # Apply reformulation:
        minimal_data_reformulation = minify_json(reformulate_text)
        reformulated_text = self._invoke_llm(minimal_data_reformulation, task="reformulation")

        # Join all results
        corrected_text = corrected_syntax + reformulated_text

        # Apply these corrections and generate the output json object
        correction_results = apply_changes(data, corrected_text)

        return correction_results

    def correct_syntax(self, data: List[InputTextEntryMinimal]) -> List[OutputChangedResult]:
        """
        Syntax correction: performs syntax correction.
        Args:
            data : List[InputTextEntryMinimal]
        Output
            correction_results: List[OutputCorrectedText]
        """
        # Apply syntax corrections:
        #   (1) transform data into minimal expression,
        #   (2) generate prompt
        #   (3) send to LLM or SLM
        minimal_data_syntax = minify_json(data)
        corrected_syntax = self._invoke_llm(minimal_data_syntax, task="syntax")

        # Apply these corrections and generate the output json object
        correction_results = apply_changes(data, corrected_syntax)

        return correction_results

    def reformulate(self, data: List[InputTextEntryMinimal]) -> List[OutputChangedResult]:
        """
        Reformulates each text segment.
        Args:
            data : List[InputTextEntryMinimal]
        Output
            correction_results: List[OutputCorrectedText]
        """
        # Apply reformulation:
        #   (1) transform data into minimal expression,
        #   (2) generate prompt
        #   (3) send to LLM or SLM
        minimal_data_reformulation = minify_json(data)
        reformulated = self._invoke_llm(minimal_data_reformulation, task="reformulation")

        # Apply these corrections and generate the output json object
        correction_results = apply_changes(data, reformulated)

        return correction_results

    def correct_and_compare(self, data: List[InputTextEntry]) -> List[OutputCompareResult]:
        """The method applied the correct method and then returns the corrected text as well as the original text.
        Args:
            data: List[InputTextEntry]
        Output:
            correction_results: List[OutputCompareResult]"""
        # Correct as usual
        data_corrected = self.correct(data)

        # Create a lookup dictionary
        lookup_dict = {entry["text_id"]: entry["text"] for entry in data}

        # Add original text for comparison
        for correct_entry in data_corrected:
            # Match by text_id
            if correct_entry.text_id in lookup_dict:
                correct_entry.original_text = lookup_dict[correct_entry.text_id]
            else:
                logging.warning("No matching text_id {correct_entry.text_id}. The LLM might have created a new text_id "
                                "not present in the original input data.")
        return data_corrected

    def _get_llm(self) -> ChatOpenAI:
        """Get or create cached LLM instance (optimization)."""
        if self._llm_cache is None:
            # API_KEY is read from env file (only once)
            load_dotenv()
            
            self._llm_cache = ChatOpenAI(
                model_name=self.model_name,
                temperature=self.temperature,
                max_completion_tokens=self.max_completion_tokens,
                openai_api_key=os.getenv("API_KEY"),
                openai_api_base=self.generative_engine_openai_api_url,
            )
        
        return self._llm_cache
    
    def _invoke_llm(self, data: List[List], task="syntax") -> List[List]:
        """
        Create a chat open AI instance to call the LLM for correcting, reformulating or translating the text in data.
        First, it estimates the number of tokens in the prompt to decide whether to send data in chunks
        or not. Then it calls the LLM on each chunk.
        Args:
            data : list of lists containing text to correct
            task: type of correction to implement
        Output:
            list of lists containing text id and the modified text
        """
        # ✨ OPTIMIZATION: Reuse cached LLM instance
        llm = self._get_llm()

        # ✨ OPTIMIZATION: Estimate tokens more efficiently
        token_count = self._estimate_tokens_fast(data, task)

        # ✨ PROTECTION: Handle empty data
        if not data or len(data) == 0:
            return []

        # If tokens exceed max limit send data in chunks
        tokenized = False
        if token_count > self.max_tokens_allowed:
            response_content = []
            lines_number = len(data)
            # ✨ OPTIMIZATION: Prevent division by zero
            estimated_tokens_per_line = max(1, token_count // lines_number)
            n_lines_accepted_in_chunk = max(1, self.max_tokens_allowed // estimated_tokens_per_line)
            n_chunks = (lines_number + n_lines_accepted_in_chunk - 1) // n_lines_accepted_in_chunk  # Ceiling division
            
            for i in range(n_chunks):
                print(f"Analyzing chunk {i}/{n_chunks}")
                start_idx = i * n_lines_accepted_in_chunk
                end_idx = min(lines_number, (i + 1) * n_lines_accepted_in_chunk)
                data_chunk = data[start_idx:end_idx]
                
                prompt = generate_prompt(data_chunk, task=task, language=self.language,
                                         prompt_task_message=str(self.prompt_task_message))
                try:
                    ai_response = llm.invoke(prompt)
                    response_content.append(ai_response.content)
                except Exception as e:
                    raise RuntimeError(f"LLM API call failed for chunk {i}/{n_chunks}: {type(e).__name__}: {e}")
            tokenized = True
        else:
            prompt = generate_prompt(data, task=task, language=self.language,
                                     prompt_task_message=str(self.prompt_task_message))
            try:
                ai_response = llm.invoke(prompt)
            except Exception as e:
                raise RuntimeError(f"LLM API call failed: {type(e).__name__}: {e}. Check API_KEY and GEN_ENG_OPENAI_API_URL configuration.")
            # ✨ OPTIMIZATION: Parse response once with cleanup
            try:
                # Clean response: remove markdown code blocks, normalize quotes/dashes
                cleaned_content = ai_response.content.strip()
                if cleaned_content.startswith("```"):
                    # Remove markdown code blocks
                    lines = cleaned_content.split("\n")
                    cleaned_content = "\n".join(lines[1:-1] if lines[-1].strip() == "```" else lines[1:])
                
                # Remove problematic line breaks inside the list (Claude sometimes breaks long responses)
                cleaned_content = cleaned_content.replace("\n", " ")
                
                # Normalize Unicode characters that break ast.literal_eval
                cleaned_content = cleaned_content.replace("–", "-").replace("—", "-")
                cleaned_content = cleaned_content.replace("'", "'").replace("'", "'")
                cleaned_content = cleaned_content.replace(""", '"').replace(""", '"')
                
                response_content = ast.literal_eval(cleaned_content)
            except (ValueError, SyntaxError) as e:
                # Show more context for debugging
                preview = ai_response.content[:500] if len(ai_response.content) > 500 else ai_response.content
                raise ValueError(f"Failed to parse LLM response: {e}\n\nResponse preview:\n{preview}")
        
        # ✨ OPTIMIZATION: Unified response processing
        if tokenized:
            try:
                parsed_lists = [ast.literal_eval(item) for item in response_content]
                flat_list_corrected = [inner for outer in parsed_lists for inner in outer]
                self._sanity_check_text_ids(original_data=data, llm_results=flat_list_corrected)
                return flat_list_corrected
            except (ValueError, SyntaxError) as e:
                raise ValueError(f"Sanity check failed: {e}")
        else:
            try:
                self._sanity_check_text_ids(original_data=data, llm_results=response_content)
                return response_content
            except ValueError as e:
                raise ValueError(f"Sanity check failed: {e}")


    def _estimate_tokens_fast(self, data: List[List], task="syntax") -> int:
        """
        Fast token estimation using cached encoding (optimization).
        Args:
            data: list of lists containing prompt human message
            task: type of correction/reformulation for LLM
        Returns:
            int: Estimated token count
        """
        # ✨ OPTIMIZATION: Use cached encoding
        if self._encoding_cache is None:
            self._encoding_cache = tiktoken.get_encoding(self.model_encoding)
        
        # ✨ OPTIMIZATION: Estimate without generating full prompt first
        # Rough estimation: count characters in data + task overhead
        data_chars = sum(len(str(item)) for item in data)
        # Task overhead is typically ~200-500 tokens depending on prompt template
        task_overhead = 500
        
        # Quick estimation: ~4 chars per token (average for most languages)
        estimated_tokens = (data_chars // 4) + task_overhead
        
        return estimated_tokens
    
    def _estimate_tokens(self, data: List[List], task="syntax") -> None:
        """
        Precise token estimation based on the LLM model encoding (backward compatibility).
        Args:
            data: list of lists containing prompt human message
            task: type of correction/reformulation for LLM
        """
        prompt = generate_prompt(data, task=task, language=self.language, prompt_task_message=str(self.prompt_task_message))
        full_text = "".join([
            f"{prompt[0].type}:{prompt[0].content}",
            f"{prompt[1].type}:{prompt[1].content}"
        ])
        # ✨ OPTIMIZATION: Use cached encoding
        if self._encoding_cache is None:
            self._encoding_cache = tiktoken.get_encoding(self.model_encoding)
        
        self.tokens = self._encoding_cache.encode(full_text)

    @staticmethod
    def _sanity_check_text_ids(
            original_data: List[List[str]], llm_results: List[List[str]]) -> None:
        """
        Validate text_ids with detailed error reporting.
        Args:
            original_data (List[List[str]]): The list of original input text entries.
            llm_results (List[List[str]]): The list of results from the LLM.
        """
        original_ids = {entry[0] for entry in original_data}

        # Extract LLM text_ids
        llm_ids = {result[0] for result in llm_results if isinstance(result, list) and len(result) > 0}

        extra_ids = llm_ids - original_ids
        missing_ids = original_ids - llm_ids

        # Build comprehensive error message
        errors = []

        if extra_ids:
            errors.append(
            f"LLM created {len(extra_ids)} new text_id(s): {sorted(extra_ids)}"
            )

        if missing_ids:
            errors.append(
                f"LLM forgot {len(missing_ids)} text_id(s): {sorted(missing_ids)}"
            )

        if errors:
            error_message = "Text ID validation failed:\n" + "\n".join(f"  - {e}" for e in errors)
            print(original_data, llm_results)
            raise ValueError(error_message)

    def translate(self, data: List[InputTextEntryMinimal], target_language: str="English") -> List[OutputChangedResult]:
        """
        Translation: translates the text in data to the language specified.
        Args:
            data : List[InputTextEntryMinimal]
        Output
            correction_results: List[OutputCorrectedText]
        """
        # Translate:
        #   (1) transform data into minimal expression,
        #   (2) generate prompt
        #   (3) send to LLM or SLM
        minimal_data_translate = minify_json(data)
        translated = self._invoke_llm(minimal_data_translate, task="translation")

        # Apply these corrections and generate the output json object
        correction_results = apply_changes(data, translated)

        return correction_results
"""
Test pipeline for textaicheck library - Complete document processing with inference time measurement.

This script:
1. Extracts text from PDF or Word documents
2. Processes the extracted document through all correction modes
3. Measures extraction and inference times separately

Extraction time and inference time are measured and reported separately.
"""

import json
import sys
import time
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime
from textaicheck.text_checkers import AdvancedTextChecker

# Import extractors from libs/extractor
sys.path.insert(0, str(Path(__file__).parent.parent / "extractor"))
from pdf_extractor.pdf_extractor import PDFExtractor
from word_extractor.WordExtractor import WordDocumentExtractor


class DocumentTestPipeline:
    """Pipeline for testing textaicheck on complete documents with performance metrics."""
    
    def __init__(self, language: str = "English"):
        """
        Initialize the test pipeline.
        
        Args:
            language (str): Primary language for processing (default: "English")
        """
        self.language = language
        self.checker = AdvancedTextChecker(language=language)
        self.results = {
            "test_date": datetime.now().isoformat(),
            "language": language,
            "extraction": {},
            "modes": {}
        }
    
    def extract_document(self, file_path: str, output_dir: Optional[str] = None) -> tuple[Dict[str, Any], str]:
        """
        Extract text from PDF or Word document.
        
        Args:
            file_path (str): Path to the PDF or Word document
            output_dir (str): Directory to save extracted JSON (optional)
            
        Returns:
            tuple: (document_data, extraction_json_path)
        """
        file_path_obj = Path(file_path)
        file_ext = file_path_obj.suffix.lower()
        
        print(f"\nExtracting document: {file_path}")
        print(f"   File type: {file_ext}")
        
        extraction_start = time.time()
        
        try:
            if file_ext == ".pdf":
                # Use PDFExtractor class
                if output_dir:
                    extractor = PDFExtractor(save_images=False, output_dir=output_dir)
                else:
                    extractor = PDFExtractor(save_images=False)
                
                document = extractor.extract_pdf_content(file_path)
                
            elif file_ext in [".docx", ".doc"]:
                # Use WordDocumentExtractor class
                extractor = WordDocumentExtractor()
                document = extractor.extract_to_json(file_path)
                
            else:
                raise ValueError(f"Unsupported file type: {file_ext}. Supported: .pdf, .docx, .doc")
            
            extraction_end = time.time()
            extraction_time = extraction_end - extraction_start
            
            # Count extracted text entries
            text_count = len(document.get("content", {}).get("text", []))
            
            self.results["extraction"] = {
                "success": True,
                "file_path": str(file_path),
                "file_type": file_ext,
                "extraction_time_seconds": round(extraction_time, 3),
                "text_entries_extracted": text_count
            }
            
            print(f"   ✅ Extraction completed in {extraction_time:.3f}s")
            print(f"   Extracted {text_count} text entries")
            
            # Save extracted JSON
            if output_dir:
                output_dir_path = Path(output_dir)
                output_dir_path.mkdir(parents=True, exist_ok=True)
                
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                json_filename = f"extracted_{file_path_obj.stem}_{timestamp}.json"
                json_path = output_dir_path / json_filename
                
                with open(json_path, 'w', encoding='utf-8') as f:
                    json.dump(document, f, indent=2, ensure_ascii=False)
                
                print(f"   Saved extracted JSON to: {json_path}")
                self.results["extraction"]["json_path"] = str(json_path)
                return document, str(json_path)
            
            return document, None
            
        except Exception as e:
            extraction_end = time.time()
            extraction_time = extraction_end - extraction_start
            
            self.results["extraction"] = {
                "success": False,
                "file_path": str(file_path),
                "file_type": file_ext,
                "extraction_time_seconds": round(extraction_time, 3),
                "error": str(e)
            }
            
            print(f"   Extraction failed: {e}")
            raise
    
    def load_document(self, file_path: str) -> Dict[str, Any]:
        """
        Load a pre-extracted document from JSON file.
        
        Args:
            file_path (str): Path to the extracted document JSON
            
        Returns:
            dict: Document data
        """
        with open(file_path, 'r', encoding='utf-8') as f:
            document = json.load(f)
        
        print(f"Loaded document: {file_path}")
        
        # Count text entries
        text_count = len(document.get("content", {}).get("text", []))
        print(f"   Total text entries: {text_count}")
        
        return document
    
    def prepare_textaicheck_input(self, document: Dict[str, Any]) -> List[Dict[str, str]]:
        """
        Convert document to textaicheck input format.
        
        Args:
            document (dict): Document data
            
        Returns:
            list: List of InputTextEntryMinimal dictionaries
        """
        textaicheck_input = []
        text_entries = document.get("content", {}).get("text", [])
        
        for idx, entry in enumerate(text_entries):
            text = entry.get("text", "")
            if text.strip():  # Skip empty texts
                textaicheck_input.append({
                    "text": text,
                    "text_id": str(idx)
                })
        
        return textaicheck_input
    
    def test_syntax_correction(self, data: List[Dict[str, str]]) -> Dict[str, Any]:
        """
        Test syntax correction mode and measure inference time.
        
        Args:
            data (list): Input data for textaicheck
            
        Returns:
            dict: Results with timing information
        """
        print("\nTesting SYNTAX correction...")
        
        start_time = time.time()
        try:
            results = self.checker.correct_syntax(data)
            end_time = time.time()
            
            inference_time = end_time - start_time
            
            # Analyze corrections: compare original vs modified
            corrections_details = []
            original_dict = {item["text_id"]: item["text"] for item in data}
            
            for r in results:
                original_text = original_dict.get(r.text_id, "")
                modified_text = r.modified_text
                
                if original_text != modified_text:
                    corrections_details.append({
                        "text_id": r.text_id,
                        "original_text": original_text,
                        "modified_text": modified_text,
                        "has_changes": True
                    })
                else:
                    corrections_details.append({
                        "text_id": r.text_id,
                        "original_text": original_text,
                        "modified_text": modified_text,
                        "has_changes": False
                    })
            
            changes_count = sum(1 for c in corrections_details if c["has_changes"])
            
            return {
                "success": True,
                "inference_time_seconds": round(inference_time, 3),
                "text_count": len(data),
                "corrections_count": len(results),
                "changes_count": changes_count,
                "avg_time_per_text": round(inference_time / len(data), 3) if data else 0,
                "corrections_details": corrections_details
            }
        except Exception as e:
            end_time = time.time()
            return {
                "success": False,
                "error": str(e),
                "inference_time_seconds": round(end_time - start_time, 3)
            }
    
    def test_reformulation(self, data: List[Dict[str, str]]) -> Dict[str, Any]:
        """
        Test reformulation mode and measure inference time.
        
        Args:
            data (list): Input data for textaicheck
            
        Returns:
            dict: Results with timing information
        """
        print("\nTesting REFORMULATION...")
        
        start_time = time.time()
        try:
            results = self.checker.reformulate(data)
            end_time = time.time()
            
            inference_time = end_time - start_time
            
            # Analyze reformulations: compare original vs reformulated
            reformulations_details = []
            original_dict = {item["text_id"]: item["text"] for item in data}
            
            for r in results:
                original_text = original_dict.get(r.text_id, "")
                modified_text = r.modified_text
                
                if original_text != modified_text:
                    reformulations_details.append({
                        "text_id": r.text_id,
                        "original_text": original_text,
                        "reformulated_text": modified_text,
                        "has_changes": True
                    })
                else:
                    reformulations_details.append({
                        "text_id": r.text_id,
                        "original_text": original_text,
                        "reformulated_text": modified_text,
                        "has_changes": False
                    })
            
            changes_count = sum(1 for c in reformulations_details if c["has_changes"])
            
            return {
                "success": True,
                "inference_time_seconds": round(inference_time, 3),
                "text_count": len(data),
                "corrections_count": len(results),
                "changes_count": changes_count,
                "avg_time_per_text": round(inference_time / len(data), 3) if data else 0,
                "reformulations_details": reformulations_details
            }
        except Exception as e:
            end_time = time.time()
            return {
                "success": False,
                "error": str(e),
                "inference_time_seconds": round(end_time - start_time, 3)
            }
    
    def test_translation(self, data: List[Dict[str, str]], target_language: str = "French") -> Dict[str, Any]:
        """
        Test translation mode and measure inference time.
        
        Args:
            data (list): Input data for textaicheck
            target_language (str): Target language for translation
            
        Returns:
            dict: Results with timing information
        """
        print(f"\nTesting TRANSLATION to {target_language}...")
        
        start_time = time.time()
        try:
            results = self.checker.translate(data, target_language=target_language)
            end_time = time.time()
            
            inference_time = end_time - start_time
            
            # Analyze translations: compare original vs translated
            translations_details = []
            original_dict = {item["text_id"]: item["text"] for item in data}
            
            for r in results:
                original_text = original_dict.get(r.text_id, "")
                translated_text = r.modified_text
                
                translations_details.append({
                    "text_id": r.text_id,
                    "original_text": original_text,
                    "translated_text": translated_text,
                    "target_language": target_language
                })
            
            return {
                "success": True,
                "target_language": target_language,
                "inference_time_seconds": round(inference_time, 3),
                "text_count": len(data),
                "corrections_count": len(results),
                "avg_time_per_text": round(inference_time / len(data), 3) if data else 0,
                "translations_details": translations_details
            }
        except Exception as e:
            end_time = time.time()
            return {
                "success": False,
                "error": str(e),
                "inference_time_seconds": round(end_time - start_time, 3)
            }
    
    def test_combined_correction(self, data: List[Dict[str, str]]) -> Dict[str, Any]:
        """
        Test combined correction mode (syntax + reformulation) and measure inference time.
        
        Args:
            data (list): Input data for textaicheck
            
        Returns:
            dict: Results with timing information
        """
        print("\nTesting COMBINED correction (syntax + reformulation)...")
        
        # Prepare InputTextEntry format with correction_type
        combined_data = []
        for item in data:
            combined_data.append({
                "text": item["text"],
                "text_id": item["text_id"],
                "correction_type": ["syntax", "reformulation"]
            })
        
        start_time = time.time()
        try:
            results = self.checker.correct(combined_data)
            end_time = time.time()
            
            inference_time = end_time - start_time
            
            # Analyze combined corrections: compare original vs corrected
            combined_details = []
            original_dict = {item["text_id"]: item["text"] for item in data}
            
            for r in results:
                original_text = original_dict.get(r.text_id, "")
                modified_text = r.modified_text
                
                if original_text != modified_text:
                    combined_details.append({
                        "text_id": r.text_id,
                        "original_text": original_text,
                        "corrected_text": modified_text,
                        "has_changes": True,
                        "correction_types": ["syntax", "reformulation"]
                    })
                else:
                    combined_details.append({
                        "text_id": r.text_id,
                        "original_text": original_text,
                        "corrected_text": modified_text,
                        "has_changes": False,
                        "correction_types": ["syntax", "reformulation"]
                    })
            
            changes_count = sum(1 for c in combined_details if c["has_changes"])
            
            return {
                "success": True,
                "inference_time_seconds": round(inference_time, 3),
                "text_count": len(data),
                "corrections_count": len(results),
                "changes_count": changes_count,
                "avg_time_per_text": round(inference_time / len(data), 3) if data else 0,
                "combined_details": combined_details
            }
        except Exception as e:
            end_time = time.time()
            return {
                "success": False,
                "error": str(e),
                "inference_time_seconds": round(end_time - start_time, 3)
            }
    
    def run_full_pipeline(self, input_path: str, output_dir: str = "test_results", 
                         test_modes: List[str] = None, target_language: str = "French") -> Dict[str, Any]:
        """
        Run complete test pipeline on a document.
        
        Args:
            input_path (str): Path to PDF/Word document OR extracted JSON file
            output_dir (str): Directory to save results
            test_modes (list): List of modes to test (default: ["syntax", "reformulation", "combined"])
            target_language (str): Target language for translation
            
        Returns:
            dict: Complete test results
        """
        print("="*80)
        print("TEXTAICHECK DOCUMENT TEST PIPELINE")
        print("="*80)
        
        # Default test modes
        if test_modes is None:
            test_modes = ["syntax", "reformulation", "combined"]
        
        input_path_obj = Path(input_path)
        file_ext = input_path_obj.suffix.lower()
        
        # Check if input is a document or already extracted JSON
        if file_ext in [".pdf", ".docx", ".doc"]:
            # Extract document first
            document, json_path = self.extract_document(input_path, output_dir=output_dir)
        elif file_ext == ".json":
            # Load already extracted JSON (extraction time not counted)
            print(f"\nLoading pre-extracted JSON: {input_path}")
            document = self.load_document(input_path)
            self.results["extraction"] = {
                "success": True,
                "file_path": str(input_path),
                "file_type": ".json",
                "extraction_time_seconds": 0,
                "text_entries_extracted": len(document.get("content", {}).get("text", [])),
                "note": "Pre-extracted JSON provided, extraction time not measured"
            }
        else:
            raise ValueError(f"Unsupported file type: {file_ext}. Supported: .pdf, .docx, .doc, .json")
        
        # Prepare input
        print("\nPreparing textaicheck input...")
        textaicheck_input = self.prepare_textaicheck_input(document)
        print(f"   Prepared {len(textaicheck_input)} text entries for processing")
        
        if not textaicheck_input:
            print("\nNo valid text entries found in document")
            return {"error": "No valid text entries"}
        
        # Run tests for selected modes
        total_start = time.time()
        
        # 1. Syntax correction
        if "syntax" in test_modes:
            self.results["modes"]["syntax"] = self.test_syntax_correction(textaicheck_input)
            if self.results["modes"]["syntax"]["success"]:
                print(f"   ✅ Completed in {self.results['modes']['syntax']['inference_time_seconds']}s")
            else:
                print(f"   Failed: {self.results['modes']['syntax'].get('error', 'Unknown error')}")
        
        # 2. Reformulation
        if "reformulation" in test_modes:
            self.results["modes"]["reformulation"] = self.test_reformulation(textaicheck_input)
            if self.results["modes"]["reformulation"]["success"]:
                print(f"   ✅ Completed in {self.results['modes']['reformulation']['inference_time_seconds']}s")
            else:
                print(f"   Failed: {self.results['modes']['reformulation'].get('error', 'Unknown error')}")
        
        # 3. Combined
        if "combined" in test_modes:
            self.results["modes"]["combined"] = self.test_combined_correction(textaicheck_input)
            if self.results["modes"]["combined"]["success"]:
                print(f"   ✅ Completed in {self.results['modes']['combined']['inference_time_seconds']}s")
            else:
                print(f"   Failed: {self.results['modes']['combined'].get('error', 'Unknown error')}")
        
        # 4. Translation
        if "translation" in test_modes:
            self.results["modes"]["translation"] = self.test_translation(textaicheck_input, target_language)
            if self.results["modes"]["translation"]["success"]:
                print(f"   ✅ Completed in {self.results['modes']['translation']['inference_time_seconds']}s")
            else:
                print(f"   Failed: {self.results['modes']['translation'].get('error', 'Unknown error')}")
        
        total_end = time.time()
        total_inference_time = total_end - total_start
        
        # Calculate summary statistics
        extraction_time = self.results["extraction"].get("extraction_time_seconds", 0)
        
        self.results["summary"] = {
            "extraction_time_seconds": extraction_time,
            "total_inference_time_seconds": round(total_inference_time, 3),
            "total_pipeline_time_seconds": round(extraction_time + total_inference_time, 3),
            "total_text_entries": len(textaicheck_input),
            "modes_tested": len(self.results["modes"]),
            "successful_modes": sum(1 for m in self.results["modes"].values() if m.get("success", False))
        }
        
        # Save results
        output_path = self._save_results(input_path, output_dir)
        
        # Print summary
        self._print_summary()
        
        print(f"\nResults saved to: {output_path}")
        print("="*80)
        
        return self.results
    
    def _save_results(self, input_path: str, output_dir: str) -> Path:
        """Save test results to JSON file."""
        output_dir_path = Path(output_dir)
        output_dir_path.mkdir(parents=True, exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        input_name = Path(input_path).stem
        output_file = output_dir_path / f"test_results_{input_name}_{timestamp}.json"
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(self.results, f, indent=2, ensure_ascii=False)
        
        return output_file
    
    def _print_summary(self):
        """Print summary of test results."""
        print("\n" + "="*80)
        print("TEST SUMMARY")
        print("="*80)
        
        summary = self.results["summary"]
        extraction = self.results.get("extraction", {})
        
        # Extraction info
        if extraction.get("success"):
            print(f"\nExtraction Time: {extraction.get('extraction_time_seconds', 0)}s")
            print(f"   File: {Path(extraction.get('file_path', '')).name}")
            print(f"   Type: {extraction.get('file_type', 'unknown')}")
            print(f"   Entries: {extraction.get('text_entries_extracted', 0)}")
        
        # Inference info
        print(f"\nTotal Inference Time: {summary['total_inference_time_seconds']}s")
        print(f"Total Pipeline Time: {summary['total_pipeline_time_seconds']}s")
        print(f"   (Extraction: {summary['extraction_time_seconds']}s + Inference: {summary['total_inference_time_seconds']}s)")
        
        print(f"\nTotal Text Entries: {summary['total_text_entries']}")
        print(f"Modes Tested: {summary['modes_tested']}")
        print(f"✅ Successful: {summary['successful_modes']}/{summary['modes_tested']}")
        
        print("\nInference Time by Mode:")
        for mode, data in self.results["modes"].items():
            if data.get("success"):
                time_sec = data["inference_time_seconds"]
                avg_time = data.get("avg_time_per_text", 0)
                count = data.get("text_count", 0)
                print(f"   • {mode.upper():15s}: {time_sec:8.3f}s (avg: {avg_time:.3f}s per text, {count} entries)")
            else:
                print(f"   • {mode.upper():15s}: FAILED - {data.get('error', 'Unknown error')}")


def main():
    """Main entry point for test pipeline."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Test textaicheck pipeline on a document")
    parser.add_argument(
        "--input", "-i",
        type=str,
        required=True,
        help="Path to PDF, Word document, or extracted JSON file"
    )
    parser.add_argument(
        "--output", "-o",
        type=str,
        default="test_results",
        help="Output directory for results (default: test_results)"
    )
    parser.add_argument(
        "--language", "-l",
        type=str,
        default="English",
        help="Primary language for processing (default: English)"
    )
    parser.add_argument(
        "--modes", "-m",
        type=str,
        nargs="+",
        choices=["syntax", "reformulation", "translation", "combined"],
        default=["syntax", "reformulation", "combined"],
        help="Correction modes to test (default: syntax reformulation combined)"
    )
    parser.add_argument(
        "--target-language",
        type=str,
        default="French",
        help="Target language for translation (default: French)"
    )
    
    args = parser.parse_args()
    
    # Verify input file exists
    if not Path(args.input).exists():
        print(f"Error: Input file not found: {args.input}")
        sys.exit(1)
    
    # Run pipeline
    pipeline = DocumentTestPipeline(language=args.language)
    results = pipeline.run_full_pipeline(
        input_path=args.input,
        output_dir=args.output,
        test_modes=args.modes,
        target_language=args.target_language
    )
    
    # Exit with status code
    if results.get("summary", {}).get("successful_modes", 0) > 0:
        sys.exit(0)
    else:
        sys.exit(1)


if __name__ == "__main__":
    main()

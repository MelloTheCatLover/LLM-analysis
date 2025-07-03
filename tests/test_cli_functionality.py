#!/usr/bin/env python3
"""
Test CLI functionality without requiring LLM
"""

import sys
import os
import tempfile
import json
from unittest.mock import patch, MagicMock

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def test_cli_classify_command():
    """Test classify command with mocked LLM"""
    print("Testing classify command...")
    
    # Mock the LLM response
    mock_response = "Категория: 1.1 диплом с отличием\nОписание: Диплом бакалавра с отличием"
    
    with patch('src.processors.llm_client.subprocess.run') as mock_run:
        # Mock the subprocess response
        mock_process = MagicMock()
        mock_process.stdout.decode.return_value = mock_response
        mock_process.stderr.decode.return_value = ""
        mock_run.return_value = mock_process
        
        # Mock OCR to return some text
        with patch('src.processors.ocr.extract_text') as mock_ocr:
            mock_ocr.return_value = "Sample document text for testing"
            
            # Import and test the classify function
            from src.cli import classify_command
            from argparse import Namespace
            
            args = Namespace(document_path="test.pdf")
            
            try:
                classify_command(args)
                print("Classify command test passed")
                return True
            except Exception as e:
                print(f"Classify command test failed: {e}")
                return False

def test_cli_extract_name_command():
    """Test extract-name command with mocked LLM"""
    print("testing extract-name command...")
    
    # Mock the LLM response
    mock_response = '{"full_name": "Иван Иванов", "match_with_expected": true, "comment": "Name found"}'
    
    with patch('src.processors.llm_client.subprocess.run') as mock_run:
        # Mock the subprocess response
        mock_process = MagicMock()
        mock_process.stdout.decode.return_value = mock_response
        mock_process.stderr.decode.return_value = ""
        mock_run.return_value = mock_process
        
        # Mock OCR to return some text
        with patch('src.processors.ocr.extract_text') as mock_ocr:
            mock_ocr.return_value = "Sample document text for testing"
            
            # Import and test the extract_name function
            from src.cli import extract_name_command
            from argparse import Namespace
            
            args = Namespace(document_path="test.pdf", expected_name="Иван Иванов")
            
            try:
                extract_name_command(args)
                print("Extract-name command test passed")
                return True
            except Exception as e:
                print(f"Extract-name command test failed: {e}")
                return False

def test_cli_check_match_command():
    """Test check-match command with mocked LLM"""
    print("Testing check-match command...")
    
    # Mock the LLM response
    mock_response = "Категория: 1.1 диплом с отличием\nОписание: Диплом бакалавра с отличием"
    
    with patch('src.processors.llm_client.subprocess.run') as mock_run:
        # Mock the subprocess response
        mock_process = MagicMock()
        mock_process.stdout.decode.return_value = mock_response
        mock_process.stderr.decode.return_value = ""
        mock_run.return_value = mock_process
        
        # Mock OCR to return some text
        with patch('src.processors.ocr.extract_text') as mock_ocr:
            mock_ocr.return_value = "Sample document text for testing"
            
            # Import and test the check_match function
            from src.cli import check_match_command
            from argparse import Namespace
            
            args = Namespace(document_path="test.pdf", claimed_category="1.1 диплом с отличием")
            
            try:
                check_match_command(args)
                print("Check-match command test passed")
                return True
            except Exception as e:
                print(f"Check-match command test failed: {e}")
                return False

def test_cli_portfolio_command():
    """Test portfolio command with mocked LLM"""
    print("Testing portfolio command...")
    
    # Create a temporary manifest file
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        manifest_data = [
            {
                "filename": "test1.pdf",
                "claimed_type": "1.1 диплом с отличием"
            },
            {
                "filename": "test2.pdf", 
                "claimed_type": "2.1 статья в Q1/Q2 журнале"
            }
        ]
        json.dump(manifest_data, f)
        manifest_path = f.name
    
    try:
        # Mock the LLM response
        mock_response = "Категория: 1.1 диплом с отличием\nОписание: Диплом бакалавра с отличием"
        
        with patch('src.processors.llm_client.subprocess.run') as mock_run:
            # Mock the subprocess response
            mock_process = MagicMock()
            mock_process.stdout.decode.return_value = mock_response
            mock_process.stderr.decode.return_value = ""
            mock_run.return_value = mock_process
            
            # Mock OCR to return some text
            with patch('src.processors.ocr.extract_text') as mock_ocr:
                mock_ocr.return_value = "Sample document text for testing"
                
                # Mock file existence
                with patch('os.path.isfile') as mock_isfile:
                    mock_isfile.return_value = True
                    
                    # Mock pandas ExcelWriter to avoid mime.types issue
                    with patch('pandas.ExcelWriter') as mock_excel_writer:
                        mock_writer = MagicMock()
                        mock_excel_writer.return_value.__enter__.return_value = mock_writer
                        
                        # Import and test the portfolio function
                        from src.cli import portfolio_command
                        from argparse import Namespace
                        
                        args = Namespace(manifest_path=manifest_path)
                        
                        try:
                            portfolio_command(args)
                            print("Portfolio command test passed")
                            return True
                        except Exception as e:
                            print(f"Portfolio command test failed: {e}")
                            return False
    finally:
        # Clean up temporary file
        os.unlink(manifest_path)

def test_cli_portfolio_expected_name_propagation():
    """Test that expected_name from the first manifest entry is propagated to all documents if not set."""
    print("Testing expected_name propagation in portfolio command...")
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        manifest_data = [
            {
                "filename": "test1.pdf",
                "claimed_type": "1.1 диплом с отличием",
                "expected_name": "Иванов Иван"
            },
            {
                "filename": "test2.pdf",
                "claimed_type": "2.1 статья в Q1/Q2 журнале"
                # expected_name отсутствует
            },
            {
                "filename": "test3.pdf",
                "claimed_type": "3.1 сертификат",
                "expected_name": ""  # пустая строка
            }
        ]
        json.dump(manifest_data, f)
        manifest_path = f.name
    try:
        mock_response = "Категория: 1.1 диплом с отличием\nОписание: Диплом бакалавра с отличием"
        with patch('src.processors.llm_client.subprocess.run') as mock_run:
            mock_process = MagicMock()
            mock_process.stdout.decode.return_value = mock_response
            mock_process.stderr.decode.return_value = ""
            mock_run.return_value = mock_process
            with patch('src.processors.ocr.extract_text') as mock_ocr:
                mock_ocr.return_value = "Sample document text for testing"
                with patch('os.path.isfile') as mock_isfile:
                    mock_isfile.return_value = True
                    with patch('pandas.ExcelWriter') as mock_excel_writer:
                        mock_writer = MagicMock()
                        mock_excel_writer.return_value.__enter__.return_value = mock_writer
                        # Patch extract_person_name to check propagation
                        with patch('src.processors.name_extractor.extract_person_name') as mock_extract_name:
                            mock_extract_name.return_value = {"full_name": "Иванов Иван", "match_with_expected": True, "comment": "OK"}
                            from src.cli import portfolio_command
                            from argparse import Namespace
                            args = Namespace(manifest_path=manifest_path)
                            try:
                                portfolio_command(args)
                                # Проверяем, что extract_person_name вызывался с propagated expected_name
                                calls = mock_extract_name.call_args_list
                                # Первый документ - явно задано имя
                                assert calls[0][0][1] == "Иванов Иван"
                                # Второй и третий - должны получить propagated имя
                                assert calls[1][0][1] == "Иванов Иван"
                                assert calls[2][0][1] == "Иванов Иван"
                                print("Portfolio expected_name propagation test passed")
                                return True
                            except Exception as e:
                                print(f"Portfolio expected_name propagation test failed: {e}")
                                return False
    finally:
        os.unlink(manifest_path)

def test_full_pipeline_build_manifest_and_portfolio():
    """Test the full pipeline: build-manifest followed by portfolio processing"""
    print("Testing full pipeline: build-manifest + portfolio...")
    import io
    from argparse import Namespace
    from src.cli import build_manifest_command, portfolio_command
    # Prepare simulated user input for build-manifest
    expected_name = "Тестовый Пользователь"
    files = [
        ("test1.pdf", "Тип 1"),
        ("test2.pdf", "Тип 2")
    ]
    user_inputs = [expected_name] + [item for pair in files for item in pair] + ["",]  # end with empty filename
    user_inputs_iter = iter(user_inputs)
    def mock_input(prompt):
        return next(user_inputs_iter)
    # Use a temp file for manifest
    import tempfile
    with tempfile.NamedTemporaryFile(mode='w+', suffix='.json', delete=False) as f:
        manifest_path = f.name
    try:
        # Patch input and run build-manifest
        with patch('builtins.input', mock_input):
            args = Namespace(output_path=manifest_path)
            build_manifest_command(args)
        # Now run portfolio on the generated manifest
        mock_response = "Категория: Тип 1\nОписание: Описание типа 1"
        with patch('src.processors.llm_client.subprocess.run') as mock_run:
            mock_process = MagicMock()
            mock_process.stdout.decode.return_value = mock_response
            mock_process.stderr.decode.return_value = ""
            mock_run.return_value = mock_process
            with patch('src.processors.ocr.extract_text') as mock_ocr:
                mock_ocr.return_value = "Sample document text for testing"
                with patch('os.path.isfile') as mock_isfile:
                    mock_isfile.return_value = True
                    with patch('pandas.ExcelWriter') as mock_excel_writer:
                        mock_writer = MagicMock()
                        mock_excel_writer.return_value.__enter__.return_value = mock_writer
                        with patch('src.processors.name_extractor.extract_person_name') as mock_extract_name:
                            mock_extract_name.return_value = {"full_name": expected_name, "match_with_expected": True, "comment": "OK"}
                            args = Namespace(manifest_path=manifest_path)
                            try:
                                portfolio_command(args)
                                print("Full pipeline test passed")
                                return True
                            except Exception as e:
                                print(f"Full pipeline test failed: {e}")
                                return False
    finally:
        os.unlink(manifest_path)

def main():
    """Run all CLI functionality tests"""
    print("Testing CLI Functionality (Mocked)...")
    print("=" * 60)
    
    tests = [
        test_cli_classify_command,
        test_cli_extract_name_command,
        test_cli_check_match_command,
        test_cli_portfolio_command,
        test_cli_portfolio_expected_name_propagation,
        test_full_pipeline_build_manifest_and_portfolio,
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
        print()
    
    print("=" * 60)
    print(f"Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("All CLI functionality tests passed!")
        print("\nThe CLI interface is fully functional and ready to use.")
        print("   Note: These tests use mocked LLM responses.")
        print("   For real usage, ensure Ollama is running with appropriate models.")
    else:
        print("Some CLI functionality tests failed. Please check the errors above.")
        sys.exit(1)

if __name__ == "__main__":
    main() 
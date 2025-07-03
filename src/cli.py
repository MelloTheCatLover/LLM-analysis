#!/usr/bin/env python3
"""
CLI Interface for LLM Analysis Project

Usage:
    python -m src.cli classify <document_path>
    python -m src.cli analyze <document_path>
    python -m src.cli extract-name <document_path> [--expected-name NAME]
    python -m src.cli check-match <document_path> <claimed_category>
    python -m src.cli portfolio <manifest_path>
"""

import argparse
import os
import sys
import json
import pandas as pd
from pathlib import Path
import logging

from src.core.config_loader import load_json
from src.core.models import DocumentResult
from src.processors.ocr import extract_text
from src.processors.classifier import compute_similarity, is_match
from src.processors.llm_client import classify_with_llm
from src.processors.name_extractor import extract_person_name
from src.processors.portfolio_analyzer import analyze_portfolio

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler("data/output/app.log", encoding="utf-8"),
        logging.StreamHandler()
    ]
)


def load_configs():
    """Load configuration files"""
    try:
        tesseract_cfg = load_json("config/tesseract_config.json")
        categories = load_json("config/categories.json")
        return tesseract_cfg, categories
    except FileNotFoundError as e:
        print(f"[ERROR] Configuration file not found: {e}")
        sys.exit(1)


def ensure_output_dir():
    """Ensure output directory exists"""
    output_dir = "data/output"
    os.makedirs(output_dir, exist_ok=True)
    return output_dir


def classify_command(args):
    """Extract text, classify it using LLM, and print detected category and description"""
    print(f"[INFO] Classifying document: {args.document_path}")
    
    tesseract_cfg, categories = load_configs()
    output_dir = ensure_output_dir()
    
    # Extract text
    text = extract_text(args.document_path, tesseract_cfg["lang"])
    if not text.strip():
        print("[ERROR] No text extracted from document")
        return
    
    # Classify with LLM
    detected, description, _ = classify_with_llm(
        text, categories, tesseract_cfg.get("model", "mistral"), output_dir
    )
    
    # Print results
    print(f"\n Classification Results:")
    print(f"Document: {os.path.basename(args.document_path)}")
    print(f"Detected Category: {detected}")
    print(f"Description: {description}")
    print(f"Text Length: {len(text)} characters")


def analyze_command(args):
    """Classify the document, then run deep analysis using LLM, and print analysis summary"""
    print(f"[INFO] Analyzing document: {args.document_path}")
    
    tesseract_cfg, categories = load_configs()
    output_dir = ensure_output_dir()
    
    # Extract text
    text = extract_text(args.document_path, tesseract_cfg["lang"])
    if not text.strip():
        print("[ERROR] No text extracted from document")
        return
    
    # Classify with LLM
    detected, description, _ = classify_with_llm(
        text, categories, tesseract_cfg.get("model", "mistral"), output_dir
    )
    
    # Deep analysis (placeholder - you can extend this with more LLM analysis)
    print(f"\nDeep Analysis Results:")
    print(f"Document: {os.path.basename(args.document_path)}")
    print(f"Category: {detected}")
    print(f"Description: {description}")
    print(f"Text Length: {len(text)} characters")
    print(f"Analysis: Document appears to be a {detected.lower()}")
    print(f"   - Contains {len(text.split())} words")
    print(f"   - Language: Mixed (Russian/English)")


def extract_name_command(args):
    """Extract the person's name from the document using LLM"""
    print(f"[INFO] Extracting person name from: {args.document_path}")
    
    tesseract_cfg, categories = load_configs()
    output_dir = ensure_output_dir()
    
    # Extract text
    text = extract_text(args.document_path, tesseract_cfg["lang"])
    if not text.strip():
        print("[ERROR] No text extracted from document")
        return
    
    # Extract person name
    person_info = extract_person_name(
        text, args.expected_name, tesseract_cfg.get("model", "mistral"), output_dir
    )
    
    # Print results
    print(f"\nPerson Name Extraction Results:")
    print(f"Document: {os.path.basename(args.document_path)}")
    print(f"Extracted Name: {person_info.get('full_name', 'Not found')}")
    
    if args.expected_name:
        print(f"Expected Name: {args.expected_name}")
        match = person_info.get('match_with_expected', False)
        print(f"Match: {'Yes' if match else 'No'}")
    
    if person_info.get('comment'):
        print(f"Comment: {person_info['comment']}")


def check_match_command(args):
    """Extract text, classify with LLM, compare detected vs claimed category"""
    print(f"[INFO] Checking category match for: {args.document_path}")
    
    tesseract_cfg, categories = load_configs()
    output_dir = ensure_output_dir()
    
    # Extract text
    text = extract_text(args.document_path, tesseract_cfg["lang"])
    if not text.strip():
        print("[ERROR] No text extracted from document")
        return
    
    # Classify with LLM
    detected, description, _ = classify_with_llm(
        text, categories, tesseract_cfg.get("model", "mistral"), output_dir
    )
    
    # Compare categories
    similarity = compute_similarity(detected, args.claimed_category)
    match = is_match(detected, args.claimed_category)
    
    # Print results
    print(f"\nCategory Match Analysis:")
    print(f"Document: {os.path.basename(args.document_path)}")
    print(f" Claimed Category: {args.claimed_category}")
    print(f"Detected Category: {detected}")
    print(f"Similarity Score: {similarity:.3f}")
    print(f"Match: {'Yes' if match else 'No'}")
    print(f"Description: {description}")


def portfolio_command(args):
    """Process portfolio documents from manifest and generate reports (new logic)"""
    print(f"[INFO] Processing portfolio from manifest: {args.manifest_path}")
    try:
        manifest = load_json(args.manifest_path)
    except FileNotFoundError:
        print(f"[ERROR] Manifest file not found: {args.manifest_path}")
        return
    if not manifest or not isinstance(manifest, list) or "expected_name" not in manifest[0]:
        print("[FATAL] Manifest must start with an object containing 'expected_name'")
        return
    expected_name = manifest[0]["expected_name"].strip()
    documents = manifest[1:]
    tesseract_cfg, categories = load_configs()
    output_dir = ensure_output_dir()
    results = []
    input_dir = "data/input"
    for entry in documents:
        filename = entry["filename"]
        claimed = entry.get("claimed_type", "").strip()
        path = os.path.join(input_dir, filename)
        if not os.path.isfile(path):
            print(f"[ERROR] File not found: {path}")
            continue
        print(f"\n[INFO] Processing: {filename}")
        # 1. Извлечение текста
        text = extract_text(path, tesseract_cfg["lang"])
        if not text.strip():
            print(f"[WARNING] No text extracted from {filename}")
            continue
        # 2. Классификация
        detected, desc, _ = classify_with_llm(
            text, categories, tesseract_cfg.get("model", "mistral"), output_dir
        )
        sim = compute_similarity(detected, claimed)
        match = is_match(detected, claimed)
        # 3. Проверка ФИО
        person = extract_person_name(
            text, expected_name, tesseract_cfg.get("model", "mistral"), output_dir
        )
        fio_match = person.get("match_with_expected", False)
        # 4. Глубокий анализ только если ФИО совпало
        analysis = {}
        if fio_match:
            analysis = {"category": detected}
        results.append({
            "filename": filename,
            "claimed": claimed,
            "detected": detected,
            "description": desc,
            "similarity": sim,
            "match": match,
            "text": text,
            "person": person,
            "fio_match": fio_match,
            "analysis": analysis
        })
    if not results:
        print("[ERROR] No documents were successfully processed")
        return
    # Итоговый анализ и отчёт только по docs с fio_match==True
    filtered_results = [r for r in results if r["fio_match"]]
    summary = analyze_portfolio(filtered_results)
    # Детали в DataFrame
    df = pd.DataFrame([{
        "Файл":   r["filename"],
        "Заявлено": r["claimed"],
        "Определено": r["detected"],
        "Описание": r["description"],
        "Сходство": f"{r['similarity']:.2f}",
        "Совпадает": "Да" if r["match"] else "Нет",
        "ФИО": r["person"].get("full_name", ""),
        "ФИО совпадает": "Да" if r["fio_match"] else "Нет",
        "Комментарий ФИО": r["person"].get("comment", ""),
        "Анализ": json.dumps(r["analysis"], ensure_ascii=False) if r["fio_match"] else ""
    } for r in results])
    # Сохранение
    timestamp = pd.Timestamp.now().strftime("%Y%m%d_%H%M%S")
    excel_path = os.path.join(output_dir, f"portfolio_report_{timestamp}.xlsx")
    df.to_excel(excel_path, index=False)
    json_path = os.path.join(output_dir, f"portfolio_summary_{timestamp}.json")
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(summary, f, ensure_ascii=False, indent=2)
    print(f"\nPortfolio Analysis Complete:")
    print(f"Processed {len(results)} documents")
    print(f"Reports saved:")
    print(f"   - Excel: {excel_path}")
    print(f"   - JSON: {json_path}")


def build_manifest_command(args):
    """Interactively build a user manifest JSON file"""
    print("[INFO] Building user manifest interactively...")
    manifest = []
    # Step 1: Get expected name
    expected_name = input("Enter expected name (ФИО): ").strip()
    if not expected_name:
        print("[ERROR] Name cannot be empty.")
        return
    manifest.append({"expected_name": expected_name})
    # Step 2: Add files one by one
    while True:
        filename = input("Enter filename (or leave empty to finish): ").strip()
        if not filename:
            break
        claimed_type = input("Enter claimed type for this file: ").strip()
        if not claimed_type:
            print("[WARNING] Claimed type cannot be empty. Skipping this file.")
            continue
        manifest.append({"filename": filename, "claimed_type": claimed_type})
    if len(manifest) == 1:
        print("[INFO] No files added. Manifest not saved.")
        return
    # Step 3: Save manifest
    output_path = args.output_path or "config/user_manifest.json"
    try:
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(manifest, f, ensure_ascii=False, indent=2)
        print(f"[SUCCESS] Manifest saved to {output_path}")
    except Exception as e:
        print(f"[ERROR] Failed to save manifest: {e}")


def main():
    """Main CLI entry point"""
    parser = argparse.ArgumentParser(
        description="LLM Analysis CLI Tool",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python -m src.cli classify data/input/document.pdf
  python -m src.cli analyze data/input/document.pdf
  python -m src.cli extract-name data/input/document.pdf --expected-name "John Doe"
  python -m src.cli check-match data/input/document.pdf "1.1 диплом с отличием"
  python -m src.cli portfolio config/user_manifest.json
        """
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Classify command
    classify_parser = subparsers.add_parser('classify', help='Classify a document')
    classify_parser.add_argument('document_path', help='Path to the document file')
    
    # Analyze command
    analyze_parser = subparsers.add_parser('analyze', help='Analyze a document')
    analyze_parser.add_argument('document_path', help='Path to the document file')
    
    # Extract name command
    extract_name_parser = subparsers.add_parser('extract-name', help='Extract person name from document')
    extract_name_parser.add_argument('document_path', help='Path to the document file')
    extract_name_parser.add_argument('--expected-name', help='Expected person name for comparison')
    
    # Check match command
    check_match_parser = subparsers.add_parser('check-match', help='Check if document matches claimed category')
    check_match_parser.add_argument('document_path', help='Path to the document file')
    check_match_parser.add_argument('claimed_category', help='Claimed document category')
    
    # Portfolio command
    portfolio_parser = subparsers.add_parser('portfolio', help='Process portfolio from manifest')
    portfolio_parser.add_argument('manifest_path', help='Path to the manifest JSON file')
    
    # Build-manifest command
    build_manifest_parser = subparsers.add_parser('build-manifest', help='Interactively build a user manifest JSON file')
    build_manifest_parser.add_argument('--output-path', help='Path to save the manifest JSON file (default: config/user_manifest.json)')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    # Execute command
    try:
        if args.command == 'classify':
            classify_command(args)
        elif args.command == 'analyze':
            analyze_command(args)
        elif args.command == 'extract-name':
            extract_name_command(args)
        elif args.command == 'check-match':
            check_match_command(args)
        elif args.command == 'portfolio':
            portfolio_command(args)
        elif args.command == 'build-manifest':
            build_manifest_command(args)
    except KeyboardInterrupt:
        print("\n[INFO] Operation cancelled by user")
    except Exception as e:
        print(f"[ERROR] An error occurred: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main() 
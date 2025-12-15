"""
REG3 Import-Check CLI - Main entry point

Combines IDML extraction and validation with a positive learning feedback loop.

Usage:
    python -m src.main <command> [options]

Commands:
    learn       - Learn patterns from IDML/XLSX pairs in learning folder
    process     - Process IDML files and generate XLSX output
    check       - Validate generated XLSX against learned patterns
    validate    - Validate a single IDML/XLSX pair
    stats       - Show aggregate statistics
    list-reports - List generated reports
    clean-reports - Remove old reports
    info        - Show project information
"""

import argparse
import sys
import logging
from pathlib import Path
from typing import List, Optional
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Project directories
PROJECT_ROOT = Path(__file__).parent.parent
INPUT_DIR = PROJECT_ROOT / "input"
LEARNING_DIR = INPUT_DIR / "learning"
PROCESSING_DIR = INPUT_DIR / "processing"
OUTPUT_DIR = PROJECT_ROOT / "output"
XLSX_OUTPUT_DIR = OUTPUT_DIR / "xlsx"
REPORTS_DIR = OUTPUT_DIR / "reports"


def find_learning_pairs():
    """Find IDML/XLSX pairs in learning folder, handling subfolder structure"""
    pairs = []

    # Check for subfolder structure (IDML/ and XLSX/)
    idml_subfolder = LEARNING_DIR / "IDML"
    xlsx_subfolder = LEARNING_DIR / "XLSX"

    if idml_subfolder.exists() and xlsx_subfolder.exists():
        # Subfolder structure
        idml_files = list(idml_subfolder.glob("*.idml"))
        xlsx_files = {f.stem: f for f in xlsx_subfolder.glob("*.xlsx")}

        for idml_file in idml_files:
            # Try exact match
            if idml_file.stem in xlsx_files:
                pairs.append((idml_file, xlsx_files[idml_file.stem]))
            else:
                # Try partial match (for cases like 160-163_B614.idml -> 160-161_B614.xlsx)
                for xlsx_stem, xlsx_file in xlsx_files.items():
                    # Check if base product name matches
                    idml_base = idml_file.stem.split('_', 1)[-1] if '_' in idml_file.stem else idml_file.stem
                    xlsx_base = xlsx_stem.split('_', 1)[-1] if '_' in xlsx_stem else xlsx_stem
                    if idml_base == xlsx_base:
                        pairs.append((idml_file, xlsx_file))
                        break
    else:
        # Flat structure
        idml_files = list(LEARNING_DIR.glob("*.idml"))
        for idml_file in idml_files:
            xlsx_file = LEARNING_DIR / f"{idml_file.stem}.xlsx"
            if xlsx_file.exists():
                pairs.append((idml_file, xlsx_file))

    return pairs


def cmd_learn(args):
    """Learn patterns from IDML/XLSX pairs in learning folder"""
    from .learner import create_learner

    print("\n" + "=" * 60)
    print("LEARNING FROM REFERENCE FILES")
    print("=" * 60)
    print(f"Learning directory: {LEARNING_DIR}")
    print()

    # Check for learning files (support both flat and subfolder structure)
    idml_subfolder = LEARNING_DIR / "IDML"
    xlsx_subfolder = LEARNING_DIR / "XLSX"

    if idml_subfolder.exists():
        idml_files = list(idml_subfolder.glob("*.idml"))
        xlsx_files = list(xlsx_subfolder.glob("*.xlsx")) if xlsx_subfolder.exists() else []
    else:
        idml_files = list(LEARNING_DIR.glob("*.idml"))
        xlsx_files = list(LEARNING_DIR.glob("*.xlsx"))

    print(f"Found {len(idml_files)} IDML files")
    print(f"Found {len(xlsx_files)} XLSX files")

    if not idml_files or not xlsx_files:
        print("\nNo learning pairs found!")
        print(f"Please add IDML and matching XLSX files to: {LEARNING_DIR}")
        return 1

    # Run learning
    learner = create_learner(LEARNING_DIR, OUTPUT_DIR)
    results = learner.learn_from_pairs()

    # Show results
    print("\n" + "-" * 40)
    print("LEARNING RESULTS")
    print("-" * 40)
    print(f"Pairs processed: {results.get('pairs_processed', 0)}")
    print(f"Patterns learned: {results.get('patterns_learned', 0)}")
    print(f"Accuracy before: {results.get('accuracy_before', 0):.1f}%")
    print(f"Accuracy after:  {results.get('accuracy_after', 0):.1f}%")

    if results.get('accuracy_after', 0) > results.get('accuracy_before', 0):
        improvement = results['accuracy_after'] - results['accuracy_before']
        print(f"\n+++ Accuracy improved by {improvement:.1f}% +++")

    # Generate comparison reports
    if args.report:
        print("\nGenerating reports...")
        _generate_learning_reports()

    print("\n" + "=" * 60)
    return 0


def cmd_process(args):
    """Process IDML files and generate XLSX output"""
    from .idml_parser import parse_idml
    from .table_extractor import extract_specs_from_document
    from .text_extractor import extract_product_info
    from .xlsx_writer import write_xlsx, create_extraction_result
    from .learner import create_learner

    print("\n" + "=" * 60)
    print("PROCESSING IDML FILES")
    print("=" * 60)
    print(f"Processing directory: {PROCESSING_DIR}")
    print(f"Output directory: {XLSX_OUTPUT_DIR}")
    print()

    # Find IDML files
    idml_files = list(PROCESSING_DIR.glob("*.idml"))

    if not idml_files:
        print("No IDML files found!")
        print(f"Please add IDML files to: {PROCESSING_DIR}")
        return 1

    print(f"Found {len(idml_files)} IDML files to process")

    # Load learned knowledge if available
    learner = create_learner(LEARNING_DIR, OUTPUT_DIR)
    knowledge_summary = learner.get_learning_summary()
    if knowledge_summary['files_learned'] > 0:
        print(f"Using knowledge from {knowledge_summary['files_learned']} learned files")

    # Process each file
    XLSX_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    results = []
    success_count = 0
    error_count = 0

    for idml_path in idml_files:
        try:
            print(f"\nProcessing: {idml_path.name}")

            # Parse and extract
            document = parse_idml(idml_path)

            # Apply learned knowledge
            learner.apply_knowledge(document)

            product_info = extract_product_info(document)
            sku_specs = extract_specs_from_document(document)

            # Create result
            result = create_extraction_result(
                source_file=str(idml_path.name),
                product_info=product_info,
                sku_specs=sku_specs
            )
            results.append(result)

            # Write individual XLSX
            if args.individual:
                output_path = XLSX_OUTPUT_DIR / f"{idml_path.stem}.xlsx"
                write_xlsx([result], output_path)
                print(f"  -> {output_path.name}")

            success_count += 1

        except Exception as e:
            logger.error(f"Error processing {idml_path.name}: {e}")
            error_count += 1

    # Write combined XLSX if requested
    if args.combined and results:
        combined_path = XLSX_OUTPUT_DIR / f"combined_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
        write_xlsx(results, combined_path)
        print(f"\nCombined output: {combined_path.name}")

    # Summary
    print("\n" + "-" * 40)
    print(f"Successfully processed: {success_count}")
    print(f"Errors: {error_count}")
    print("=" * 60)

    return 0 if error_count == 0 else 1


def cmd_check(args):
    """Validate all files and generate reports"""
    from .comparator import Comparator, compare_files
    from .reporter import Reporter

    print("\n" + "=" * 60)
    print("CHECKING EXTRACTED DATA")
    print("=" * 60)

    # Find pairs in learning directory (supports subfolder structure)
    pairs = find_learning_pairs()

    if not pairs:
        print("No IDML/XLSX pairs found for validation!")
        print(f"Please add files to: {LEARNING_DIR}")
        print("  - Subfolder structure: IDML/*.idml and XLSX/*.xlsx")
        print("  - Or flat structure: *.idml and *.xlsx in same folder")
        return 1

    print(f"Found {len(pairs)} pairs to validate")

    # Compare all pairs
    comparator = Comparator()
    results = []

    for idml_path, xlsx_path in pairs:
        try:
            print(f"Validating: {idml_path.name}")
            result = compare_files(idml_path, xlsx_path)
            results.append(result)
            comparator.results.append(result)
            print(f"  Accuracy: {result.accuracy:.1f}%")
        except Exception as e:
            logger.error(f"Error validating {idml_path.name}: {e}")

    # Print summary
    from .reporter import print_comparison_summary
    print_comparison_summary(results)

    # Generate reports
    if args.report:
        REPORTS_DIR.mkdir(parents=True, exist_ok=True)
        reporter = Reporter(REPORTS_DIR)
        reports = reporter.generate_all(results, "check")

        print("Reports generated:")
        for fmt, path in reports.items():
            print(f"  {fmt}: {path.name}")

    return 0


def cmd_validate(args):
    """Validate a single IDML/XLSX pair"""
    from .comparator import compare_files
    from .reporter import Reporter

    idml_path = Path(args.idml)
    xlsx_path = Path(args.xlsx)

    if not idml_path.exists():
        print(f"IDML file not found: {idml_path}")
        return 1

    if not xlsx_path.exists():
        print(f"XLSX file not found: {xlsx_path}")
        return 1

    print("\n" + "=" * 60)
    print("VALIDATING SINGLE PAIR")
    print("=" * 60)
    print(f"IDML: {idml_path}")
    print(f"XLSX: {xlsx_path}")

    result = compare_files(idml_path, xlsx_path)

    print(f"\nAccuracy: {result.accuracy:.1f}%")
    print(f"Matches: {len(result.matches)}")
    print(f"Mismatches: {len(result.mismatches)}")
    print(f"New fields: {len(result.new_fields)}")
    print(f"Missing fields: {len(result.missing_fields)}")

    if result.mismatches and args.verbose:
        print("\nMismatches:")
        for comp in result.mismatches[:20]:
            print(f"  {comp.field_name}:")
            print(f"    Extracted: {comp.extracted_value}")
            print(f"    Expected:  {comp.reference_value}")

    if args.report:
        REPORTS_DIR.mkdir(parents=True, exist_ok=True)
        reporter = Reporter(REPORTS_DIR)
        reports = reporter.generate_all([result], f"validate_{idml_path.stem}")
        print(f"\nReports generated in: {REPORTS_DIR}")

    return 0


def cmd_stats(args):
    """Show aggregate statistics"""
    from .learner import create_learner
    import json

    print("\n" + "=" * 60)
    print("LEARNING STATISTICS")
    print("=" * 60)

    learner = create_learner(LEARNING_DIR, OUTPUT_DIR)
    summary = learner.get_learning_summary()

    print(f"Files learned: {summary['files_learned']}")
    print(f"Attribute mappings: {summary['attribute_mappings']}")
    print(f"Value transforms: {summary['value_transforms']}")
    print(f"Style mappings: {summary['style_mappings']}")
    print(f"Field patterns: {summary['field_patterns']}")
    print(f"Last updated: {summary['last_updated'] or 'Never'}")

    if summary['accuracy_history']:
        print("\nAccuracy History (last 10):")
        for entry in summary['accuracy_history']:
            print(f"  {entry['timestamp'][:10]}: {entry['accuracy']:.1f}%")

    return 0


def cmd_list_reports(args):
    """List generated reports"""
    print("\n" + "=" * 60)
    print("GENERATED REPORTS")
    print("=" * 60)

    if not REPORTS_DIR.exists():
        print("No reports directory found.")
        return 0

    reports = list(REPORTS_DIR.glob("*"))
    if not reports:
        print("No reports found.")
        return 0

    # Group by base name
    report_groups = {}
    for report in sorted(reports):
        base = report.stem.rsplit('_', 2)[0]  # Remove timestamp
        if base not in report_groups:
            report_groups[base] = []
        report_groups[base].append(report)

    for base, files in report_groups.items():
        print(f"\n{base}:")
        for f in files:
            print(f"  {f.name} ({f.stat().st_size // 1024}KB)")

    return 0


def cmd_clean_reports(args):
    """Remove old reports"""
    if not REPORTS_DIR.exists():
        print("No reports directory found.")
        return 0

    reports = list(REPORTS_DIR.glob("*"))
    if not reports:
        print("No reports to clean.")
        return 0

    if not args.force:
        print(f"Found {len(reports)} reports to delete.")
        confirm = input("Are you sure? (y/N): ")
        if confirm.lower() != 'y':
            print("Cancelled.")
            return 0

    for report in reports:
        report.unlink()
        print(f"Deleted: {report.name}")

    print(f"\nDeleted {len(reports)} reports.")
    return 0


def cmd_info(args):
    """Show project information"""
    print("\n" + "=" * 60)
    print("REG3 IMPORT-CHECK")
    print("IDML to XLSX Extractor with Learning Feedback Loop")
    print("=" * 60)

    print("\nProject Structure:")
    print(f"  Project root: {PROJECT_ROOT}")
    print(f"  Learning data: {LEARNING_DIR}")
    print(f"  Processing data: {PROCESSING_DIR}")
    print(f"  XLSX output: {XLSX_OUTPUT_DIR}")
    print(f"  Reports: {REPORTS_DIR}")

    print("\nInput Folders:")
    print("  input/learning/  - IDML + manually created XLSX pairs for learning")
    print("  input/processing/ - IDML files to process and generate XLSX")

    print("\nCommands:")
    print("  learn    - Learn patterns from reference files")
    print("  process  - Process IDML files to XLSX")
    print("  check    - Validate and generate reports")
    print("  validate - Validate a single pair")
    print("  stats    - Show learning statistics")

    print("\nWorkflow:")
    print("  1. Add IDML + XLSX pairs to input/learning/")
    print("  2. Run 'learn' to build knowledge base")
    print("  3. Add IDML files to input/processing/")
    print("  4. Run 'process' to generate XLSX files")
    print("  5. Run 'check' to validate accuracy")
    print("  6. Iterate: improve learning data and repeat")

    return 0


def _generate_learning_reports():
    """Generate reports for learning data"""
    from .comparator import compare_files
    from .reporter import Reporter

    pairs = find_learning_pairs()
    results = []

    for idml_path, xlsx_path in pairs:
        try:
            result = compare_files(idml_path, xlsx_path)
            results.append(result)
        except Exception as e:
            logger.error(f"Error comparing {idml_path.name}: {e}")

    if results:
        REPORTS_DIR.mkdir(parents=True, exist_ok=True)
        reporter = Reporter(REPORTS_DIR)
        reporter.generate_all(results, "learning")


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description="REG3 Import-Check: IDML to XLSX with Learning Feedback",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python -m src.main learn --report     Learn from files and generate reports
  python -m src.main process            Process all IDML files
  python -m src.main check --report     Validate and report
  python -m src.main validate file.idml file.xlsx
  python -m src.main stats              Show learning statistics
  python -m src.main info               Show project information
        """
    )

    subparsers = parser.add_subparsers(dest='command', help='Command to run')

    # Learn command
    learn_parser = subparsers.add_parser('learn', help='Learn from reference files')
    learn_parser.add_argument('--report', action='store_true', help='Generate reports')

    # Process command
    process_parser = subparsers.add_parser('process', help='Process IDML files')
    process_parser.add_argument('--individual', '-i', action='store_true',
                                default=True, help='Generate individual XLSX files')
    process_parser.add_argument('--combined', '-c', action='store_true',
                                help='Also generate combined XLSX')

    # Check command
    check_parser = subparsers.add_parser('check', help='Validate all files')
    check_parser.add_argument('--report', '-r', action='store_true',
                              default=True, help='Generate reports')

    # Validate command
    validate_parser = subparsers.add_parser('validate', help='Validate single pair')
    validate_parser.add_argument('idml', help='Path to IDML file')
    validate_parser.add_argument('xlsx', help='Path to XLSX file')
    validate_parser.add_argument('--verbose', '-v', action='store_true',
                                 help='Show detailed mismatches')
    validate_parser.add_argument('--report', '-r', action='store_true',
                                 help='Generate reports')

    # Stats command
    subparsers.add_parser('stats', help='Show learning statistics')

    # List reports command
    subparsers.add_parser('list-reports', help='List generated reports')

    # Clean reports command
    clean_parser = subparsers.add_parser('clean-reports', help='Remove old reports')
    clean_parser.add_argument('--force', '-f', action='store_true',
                              help='Skip confirmation')

    # Info command
    subparsers.add_parser('info', help='Show project information')

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return 0

    # Dispatch to command handler
    commands = {
        'learn': cmd_learn,
        'process': cmd_process,
        'check': cmd_check,
        'validate': cmd_validate,
        'stats': cmd_stats,
        'list-reports': cmd_list_reports,
        'clean-reports': cmd_clean_reports,
        'info': cmd_info,
    }

    handler = commands.get(args.command)
    if handler:
        return handler(args)
    else:
        parser.print_help()
        return 1


if __name__ == "__main__":
    sys.exit(main())

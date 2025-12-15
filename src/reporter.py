"""
Reporter - Generate reports in multiple formats

Output formats:
- HTML: Visual report with color-coded status
- JSON: Structured data for programmatic use
- CSV: Spreadsheet-compatible for analysis
- Text: Console output
"""

from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime
import json
import csv
import html
import logging

from .comparator import ComparisonResult, FieldComparison

logger = logging.getLogger(__name__)


class Reporter:
    """Generate reports in multiple formats"""

    def __init__(self, output_dir: Path):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def generate_all(
        self,
        results: List[ComparisonResult],
        base_name: str = "report"
    ) -> Dict[str, Path]:
        """Generate reports in all formats"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        base_name = f"{base_name}_{timestamp}"

        reports = {
            'html': self.generate_html(results, base_name),
            'json': self.generate_json(results, base_name),
            'csv': self.generate_csv(results, base_name),
            'text': self.generate_text(results, base_name)
        }

        return reports

    def generate_html(
        self,
        results: List[ComparisonResult],
        base_name: str
    ) -> Path:
        """Generate HTML report"""
        output_path = self.output_dir / f"{base_name}.html"

        # Calculate aggregate stats
        total_files = len(results)
        total_matches = sum(len(r.matches) for r in results)
        total_mismatches = sum(len(r.mismatches) for r in results)
        total_new = sum(len(r.new_fields) for r in results)
        total_missing = sum(len(r.missing_fields) for r in results)

        total_compared = total_matches + total_mismatches
        overall_accuracy = (total_matches / total_compared * 100) if total_compared > 0 else 0

        html_content = f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>REG3 Import-Check Report</title>
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, sans-serif;
            margin: 0;
            padding: 20px;
            background: #f5f5f5;
        }}
        .container {{
            max-width: 1200px;
            margin: 0 auto;
        }}
        h1 {{
            color: #333;
            border-bottom: 3px solid #4472C4;
            padding-bottom: 10px;
        }}
        .summary {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin: 20px 0;
        }}
        .stat-card {{
            background: white;
            border-radius: 8px;
            padding: 20px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}
        .stat-card h3 {{
            margin: 0 0 10px 0;
            color: #666;
            font-size: 14px;
        }}
        .stat-card .value {{
            font-size: 32px;
            font-weight: bold;
        }}
        .stat-card.accuracy .value {{
            color: {self._accuracy_color(overall_accuracy)};
        }}
        .stat-card.matches .value {{ color: #28a745; }}
        .stat-card.mismatches .value {{ color: #dc3545; }}
        .stat-card.new .value {{ color: #17a2b8; }}
        .stat-card.missing .value {{ color: #ffc107; }}
        .file-section {{
            background: white;
            border-radius: 8px;
            margin: 20px 0;
            padding: 20px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}
        .file-header {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 15px;
        }}
        .file-header h2 {{
            margin: 0;
            color: #333;
        }}
        .accuracy-badge {{
            padding: 5px 15px;
            border-radius: 20px;
            font-weight: bold;
            color: white;
        }}
        table {{
            width: 100%;
            border-collapse: collapse;
            margin-top: 10px;
        }}
        th, td {{
            padding: 10px;
            text-align: left;
            border-bottom: 1px solid #eee;
        }}
        th {{
            background: #f8f9fa;
            font-weight: 600;
        }}
        .status-match {{ color: #28a745; }}
        .status-mismatch {{ color: #dc3545; }}
        .status-new {{ color: #17a2b8; }}
        .status-missing {{ color: #ffc107; }}
        .footer {{
            text-align: center;
            padding: 20px;
            color: #666;
        }}
    </style>
</head>
<body>
    <div class="container">
        <h1>REG3 Import-Check Report</h1>
        <p>Generated: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}</p>

        <div class="summary">
            <div class="stat-card accuracy">
                <h3>Overall Accuracy</h3>
                <div class="value">{overall_accuracy:.1f}%</div>
            </div>
            <div class="stat-card">
                <h3>Files Analyzed</h3>
                <div class="value">{total_files}</div>
            </div>
            <div class="stat-card matches">
                <h3>Matches</h3>
                <div class="value">{total_matches}</div>
            </div>
            <div class="stat-card mismatches">
                <h3>Mismatches</h3>
                <div class="value">{total_mismatches}</div>
            </div>
            <div class="stat-card new">
                <h3>New Fields</h3>
                <div class="value">{total_new}</div>
            </div>
            <div class="stat-card missing">
                <h3>Missing Fields</h3>
                <div class="value">{total_missing}</div>
            </div>
        </div>

        {"".join(self._file_section_html(r) for r in results)}

        <div class="footer">
            <p>REG3 Import-Check - IDML to XLSX Extraction with Learning Feedback Loop</p>
        </div>
    </div>
</body>
</html>'''

        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(html_content)

        logger.info(f"Generated HTML report: {output_path}")
        return output_path

    def _file_section_html(self, result: ComparisonResult) -> str:
        """Generate HTML section for a single file"""
        accuracy = result.accuracy
        color = self._accuracy_color(accuracy)

        rows = []
        for comp in result.comparisons[:50]:  # Limit to 50 rows
            status_class = f"status-{comp.status}"
            rows.append(f'''
            <tr>
                <td>{html.escape(comp.field_name)}</td>
                <td>{html.escape(str(comp.extracted_value)[:100])}</td>
                <td>{html.escape(str(comp.reference_value)[:100])}</td>
                <td class="{status_class}">{comp.status.upper()}</td>
                <td>{comp.similarity:.0%}</td>
            </tr>''')

        return f'''
        <div class="file-section">
            <div class="file-header">
                <h2>{html.escape(result.idml_file)}</h2>
                <span class="accuracy-badge" style="background: {color}">{accuracy:.1f}%</span>
            </div>
            <p>Reference: {html.escape(result.xlsx_file)}</p>
            <table>
                <thead>
                    <tr>
                        <th>Field</th>
                        <th>Extracted</th>
                        <th>Reference</th>
                        <th>Status</th>
                        <th>Similarity</th>
                    </tr>
                </thead>
                <tbody>
                    {"".join(rows)}
                </tbody>
            </table>
            {f'<p><em>Showing first 50 of {len(result.comparisons)} comparisons</em></p>' if len(result.comparisons) > 50 else ''}
        </div>'''

    def _accuracy_color(self, accuracy: float) -> str:
        """Get color for accuracy value"""
        if accuracy >= 90:
            return '#28a745'  # Green
        elif accuracy >= 70:
            return '#ffc107'  # Yellow
        else:
            return '#dc3545'  # Red

    def generate_json(
        self,
        results: List[ComparisonResult],
        base_name: str
    ) -> Path:
        """Generate JSON report"""
        output_path = self.output_dir / f"{base_name}.json"

        report_data = {
            'generated': datetime.now().isoformat(),
            'summary': self._calculate_summary(results),
            'results': [r.to_dict() for r in results]
        }

        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(report_data, f, indent=2)

        logger.info(f"Generated JSON report: {output_path}")
        return output_path

    def generate_csv(
        self,
        results: List[ComparisonResult],
        base_name: str
    ) -> Path:
        """Generate CSV report"""
        output_path = self.output_dir / f"{base_name}.csv"

        with open(output_path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)

            # Header
            writer.writerow([
                'File', 'Field', 'Extracted', 'Reference', 'Status', 'Similarity'
            ])

            # Data rows
            for result in results:
                for comp in result.comparisons:
                    writer.writerow([
                        result.idml_file,
                        comp.field_name,
                        comp.extracted_value,
                        comp.reference_value,
                        comp.status,
                        f"{comp.similarity:.2f}"
                    ])

        logger.info(f"Generated CSV report: {output_path}")
        return output_path

    def generate_text(
        self,
        results: List[ComparisonResult],
        base_name: str
    ) -> Path:
        """Generate text report"""
        output_path = self.output_dir / f"{base_name}.txt"

        lines = []
        lines.append("=" * 80)
        lines.append("REG3 IMPORT-CHECK REPORT")
        lines.append("=" * 80)
        lines.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        lines.append("")

        # Summary
        summary = self._calculate_summary(results)
        lines.append("SUMMARY")
        lines.append("-" * 40)
        lines.append(f"Files Analyzed: {summary['files']}")
        lines.append(f"Overall Accuracy: {summary['accuracy']:.1f}%")
        lines.append(f"Total Matches: {summary['matches']}")
        lines.append(f"Total Mismatches: {summary['mismatches']}")
        lines.append(f"New Fields: {summary['new_fields']}")
        lines.append(f"Missing Fields: {summary['missing_fields']}")
        lines.append("")

        # Per-file details
        for result in results:
            lines.append("=" * 80)
            lines.append(f"FILE: {result.idml_file}")
            lines.append(f"Reference: {result.xlsx_file}")
            lines.append(f"Accuracy: {result.accuracy:.1f}%")
            lines.append("-" * 40)

            if result.mismatches:
                lines.append("MISMATCHES:")
                for comp in result.mismatches[:10]:
                    lines.append(f"  {comp.field_name}:")
                    lines.append(f"    Extracted: {comp.extracted_value}")
                    lines.append(f"    Expected:  {comp.reference_value}")
                if len(result.mismatches) > 10:
                    lines.append(f"  ... and {len(result.mismatches) - 10} more")

            lines.append("")

        content = "\n".join(lines)

        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(content)

        logger.info(f"Generated text report: {output_path}")
        return output_path

    def _calculate_summary(self, results: List[ComparisonResult]) -> Dict[str, Any]:
        """Calculate summary statistics"""
        total_matches = sum(len(r.matches) for r in results)
        total_mismatches = sum(len(r.mismatches) for r in results)
        total_new = sum(len(r.new_fields) for r in results)
        total_missing = sum(len(r.missing_fields) for r in results)

        total_compared = total_matches + total_mismatches
        accuracy = (total_matches / total_compared * 100) if total_compared > 0 else 0

        return {
            'files': len(results),
            'accuracy': accuracy,
            'matches': total_matches,
            'mismatches': total_mismatches,
            'new_fields': total_new,
            'missing_fields': total_missing
        }

    def print_summary(self, results: List[ComparisonResult]):
        """Print summary to console"""
        summary = self._calculate_summary(results)

        print("\n" + "=" * 60)
        print("REG3 IMPORT-CHECK SUMMARY")
        print("=" * 60)
        print(f"Files Analyzed:    {summary['files']}")
        print(f"Overall Accuracy:  {summary['accuracy']:.1f}%")
        print(f"Total Matches:     {summary['matches']}")
        print(f"Total Mismatches:  {summary['mismatches']}")
        print(f"New Fields:        {summary['new_fields']}")
        print(f"Missing Fields:    {summary['missing_fields']}")
        print("=" * 60 + "\n")


def generate_reports(
    results: List[ComparisonResult],
    output_dir: Path,
    base_name: str = "report"
) -> Dict[str, Path]:
    """Convenience function to generate all reports"""
    reporter = Reporter(output_dir)
    return reporter.generate_all(results, base_name)


def print_comparison_summary(results: List[ComparisonResult]):
    """Print summary to console"""
    reporter = Reporter(Path("."))
    reporter.print_summary(results)

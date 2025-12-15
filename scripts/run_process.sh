#!/bin/bash
# Process IDML files and generate XLSX output

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

echo "========================================"
echo "REG3 Import-Check - Process IDML Files"
echo "========================================"
echo ""

cd "$PROJECT_ROOT"

# Check for virtual environment
if [ -d "venv" ]; then
    source venv/bin/activate
    echo "Using virtual environment"
fi

# Run processing
python -m src.main process --individual --combined

echo ""
echo "Processing complete!"
echo ""
echo "Output files in: output/xlsx/"
echo ""
echo "Next steps:"
echo "  1. Download generated XLSX files"
echo "  2. Review and validate data"
echo "  3. Run 'run_check.sh' to compare with references"

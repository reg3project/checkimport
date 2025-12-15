#!/bin/bash
# Run learning cycle - learn from reference IDML/XLSX pairs

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

echo "========================================"
echo "REG3 Import-Check - Learning Cycle"
echo "========================================"
echo ""

cd "$PROJECT_ROOT"

# Check for virtual environment
if [ -d "venv" ]; then
    source venv/bin/activate
    echo "Using virtual environment"
fi

# Run learning
python -m src.main learn --report

echo ""
echo "Learning complete!"
echo ""
echo "Next steps:"
echo "  1. Review reports in output/reports/"
echo "  2. Add more learning pairs if accuracy is low"
echo "  3. Run 'run_process.sh' to process new IDML files"

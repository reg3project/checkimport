#!/bin/bash
# Run validation check and generate reports

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

echo "========================================"
echo "REG3 Import-Check - Validation Check"
echo "========================================"
echo ""

cd "$PROJECT_ROOT"

# Check for virtual environment
if [ -d "venv" ]; then
    source venv/bin/activate
    echo "Using virtual environment"
fi

# Run check
python -m src.main check --report

echo ""
echo "Validation complete!"
echo ""
echo "Reports generated in: output/reports/"

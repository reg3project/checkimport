# REG3 Import-Check

**IDML to XLSX Extractor with Positive Learning Feedback Loop**

Extract product data from Adobe InDesign IDML files (FAAC product catalog pages) and convert them into structured XLSX spreadsheets for database import. The system learns from manually created reference files to continuously improve extraction accuracy.

## Overview

This project combines two functionalities:
1. **REG3 Import**: Extract data from IDML files and generate XLSX output
2. **REG3 Check**: Validate extractions against reference files

The key innovation is the **Positive Learning Feedback Loop** that allows the system to learn from manually created XLSX files to improve extraction accuracy over time.

## Workflow

```
┌─────────────────────────────────────────────────────────────────┐
│  LEARNING DATA (input/learning/)                                │
│  ┌──────────┐     ┌──────────┐                                  │
│  │  IDML    │ ──► │  XLSX    │  (manually created reference)    │
│  └──────────┘     └──────────┘                                  │
└─────────────────────────────────────────────────────────────────┘
           │                │
           ▼                ▼
    ┌──────────────────────────────────────┐
    │     LEARN PATTERNS                   │
    │  - Attribute name mappings           │
    │  - Value transformations             │
    │  - Table structure patterns          │
    └──────────────────────────────────────┘
           │
           ▼
    ┌──────────────────────────────────────┐
    │     KNOWLEDGE BASE                   │
    │  (output/learning_data.json)         │
    └──────────────────────────────────────┘
           │
           ▼
┌─────────────────────────────────────────────────────────────────┐
│  PROCESSING DATA (input/processing/)                            │
│  ┌──────────┐                                                   │
│  │  IDML    │ ──► Apply patterns ──► Generate XLSX              │
│  └──────────┘                                                   │
└─────────────────────────────────────────────────────────────────┘
           │
           ▼
    ┌──────────────────────────────────────┐
    │     VALIDATE & IMPROVE               │
    │  - Compare with expectations         │
    │  - Track accuracy over time          │
    │  - Suggest improvements              │
    └──────────────────────────────────────┘
```

## Input Folders

### 1. Learning Data (`input/learning/`)
Place IDML files paired with manually created XLSX reference files:
- `product_page_001.idml` + `product_page_001.xlsx`
- `product_page_002.idml` + `product_page_002.xlsx`
- etc.

These pairs teach the system how to correctly extract data.

### 2. Processing Data (`input/processing/`)
Place IDML files that need to be processed:
- `new_product_001.idml`
- `new_product_002.idml`
- etc.

The system will generate XLSX files using learned patterns.

## Output

### Generated XLSX Structure

**Sheet "prodotti"** (36 columns): Product-level metadata
- category, subcategory, name, page
- description, short_description, features
- badges, certifications
- images, documents, accessories
- etc.

**Sheet "sku"** (66 columns): SKU-level technical specs
- sku, product_id, variant_name
- voltage, power, current, frequency
- motor_type, speed, torque
- weight, dimensions
- ip_rating, temperature range
- etc.

### Reports (`output/reports/`)
- **HTML**: Visual report with color-coded status
- **JSON**: Structured data for programmatic use
- **CSV**: Spreadsheet-compatible for analysis
- **Text**: Console-friendly summary

## Git Instructions

### Windows Local Setup (FAAC)

**Your local folder:** `C:\Users\Lucar\Documents\FAAC\git\checkimport`

#### First Time Clone (Open CMD or PowerShell)
```cmd
cd C:\Users\Lucar\Documents\FAAC\git
git clone https://github.com/reg3project/checkimport.git
cd checkimport
```

#### Daily Workflow

**1. Open terminal and navigate to project:**
```cmd
cd C:\Users\Lucar\Documents\FAAC\git\checkimport
```

**2. Pull latest changes from GitHub:**
```cmd
git pull origin main
```

**3. Add your IDML/XLSX files:**
```cmd
REM For learning data (training pairs)
copy "C:\path\to\your\file.idml" "input\learning\"
copy "C:\path\to\your\file.xlsx" "input\learning\"

REM For processing (new IDML files to convert)
copy "C:\path\to\your\file.idml" "input\processing\"
```

**4. Commit and push your files:**
```cmd
git add .
git status
git commit -m "Add new IDML files for processing"
git push origin main
```

**5. After Claude Code processes, pull results:**
```cmd
git pull origin main
REM Results are in: output\xlsx\ and output\reports\
```

#### Quick Reference Commands (Windows CMD)
```cmd
REM Check status
cd C:\Users\Lucar\Documents\FAAC\git\checkimport
git status

REM Pull latest
git pull origin main

REM Add all files and push
git add .
git commit -m "Your message here"
git push origin main

REM View what changed
git log --oneline -5

REM Discard local changes (careful!)
git checkout -- .
```

#### Run Processing Locally (Windows)
```cmd
cd C:\Users\Lucar\Documents\FAAC\git\checkimport

REM Create virtual environment (first time only)
python -m venv venv
venv\Scripts\activate

REM Install dependencies (first time only)
pip install -r requirements.txt

REM Run commands
python -m src.main learn --report
python -m src.main process
python -m src.main check --report
```

#### Open in File Explorer
```cmd
explorer C:\Users\Lucar\Documents\FAAC\git\checkimport\input\learning
explorer C:\Users\Lucar\Documents\FAAC\git\checkimport\input\processing
explorer C:\Users\Lucar\Documents\FAAC\git\checkimport\output\xlsx
```

---

### First Time Setup - Clone the Repository

**Option 1: HTTPS (recommended for most users)**
```bash
git clone https://github.com/reg3project/checkimport.git
cd checkimport
```

**Option 2: SSH (if you have SSH keys configured)**
```bash
git clone git@github.com:reg3project/checkimport.git
cd checkimport
```

**Option 3: GitHub CLI**
```bash
gh repo clone reg3project/checkimport
cd checkimport
```

### Pull Latest Updates

```bash
# Navigate to your local repository
cd checkimport

# Fetch and merge latest changes from main branch
git pull origin main

# Or if you're on a specific branch
git pull origin your-branch-name
```

### Working with Branches

```bash
# See all branches
git branch -a

# Create and switch to a new branch for your work
git checkout -b my-feature-branch

# Switch to an existing branch
git checkout branch-name

# Push your branch to GitHub
git push -u origin my-feature-branch
```

### Upload Files to GitHub

**Step 1: Add your files to the appropriate folder**
```bash
# For learning data (IDML + XLSX pairs)
cp your_file.idml input/learning/
cp your_file.xlsx input/learning/

# For processing (IDML files to convert)
cp your_file.idml input/processing/
```

**Step 2: Stage, commit, and push**
```bash
# Stage all new files
git add .

# Or stage specific files
git add input/learning/your_file.idml
git add input/learning/your_file.xlsx

# Commit with a descriptive message
git commit -m "Add learning data for product XYZ"

# Push to GitHub
git push origin your-branch-name
```

### Download Results from GitHub

**Option 1: Pull the entire repository**
```bash
git pull origin main
# Results will be in output/xlsx/ and output/reports/
```

**Option 2: Download specific files via GitHub web interface**
1. Go to https://github.com/reg3project/checkimport
2. Navigate to `output/xlsx/` or `output/reports/`
3. Click on the file you want
4. Click "Download" or "Raw" button

**Option 3: Use GitHub CLI**
```bash
# Download a specific file
gh api repos/reg3project/checkimport/contents/output/xlsx/your_file.xlsx --jq '.content' | base64 -d > your_file.xlsx
```

### Sync Fork with Original Repository

If you forked the repository:
```bash
# Add upstream remote (only needed once)
git remote add upstream https://github.com/reg3project/checkimport.git

# Fetch upstream changes
git fetch upstream

# Merge upstream changes into your branch
git checkout main
git merge upstream/main

# Push to your fork
git push origin main
```

### Common Git Commands Reference

| Command | Description |
|---------|-------------|
| `git status` | Check current status and changed files |
| `git log --oneline` | View commit history |
| `git diff` | See uncommitted changes |
| `git stash` | Temporarily save uncommitted changes |
| `git stash pop` | Restore stashed changes |
| `git reset --hard HEAD` | Discard all uncommitted changes |
| `git fetch --all` | Fetch all branches from remote |

---

## Installation

```bash
# Clone the repository
git clone https://github.com/reg3project/checkimport.git
cd checkimport

# Create virtual environment (recommended)
python -m venv venv
source venv/bin/activate  # Linux/Mac
# or: venv\Scripts\activate  # Windows

# Install dependencies
pip install -r requirements.txt
```

## Usage

### Command Line Interface

```bash
# Show help
python -m src.main --help

# Show project information
python -m src.main info

# Learn from reference files
python -m src.main learn --report

# Process IDML files
python -m src.main process

# Validate all learning pairs
python -m src.main check --report

# Validate a single pair
python -m src.main validate path/to/file.idml path/to/file.xlsx

# Show learning statistics
python -m src.main stats

# List generated reports
python -m src.main list-reports

# Clean old reports
python -m src.main clean-reports
```

### Helper Scripts

**Linux/Mac:**
```bash
./scripts/run_learning.sh   # Run learning cycle
./scripts/run_process.sh    # Process IDML files
./scripts/run_check.sh      # Validate and report
```

**Windows:**
```cmd
scripts\run_learning.bat
scripts\run_process.bat
scripts\run_check.bat
```

## GitHub Workflow

### Upload Files for Processing

1. Fork or clone the repository
2. Add IDML files to `input/processing/`
3. Commit and push to your branch
4. Claude Code will process files automatically
5. Download generated XLSX from `output/xlsx/`

### Improve Accuracy with Learning Data

1. Add IDML + XLSX pairs to `input/learning/`
2. Run learning cycle
3. Review accuracy reports
4. Iterate until accuracy meets requirements

## Project Structure

```
checkimport/
├── src/
│   ├── __init__.py         # Package initialization
│   ├── main.py             # CLI entry point
│   ├── idml_parser.py      # Parse IDML ZIP structure
│   ├── table_extractor.py  # Extract technical specs from tables
│   ├── text_extractor.py   # Extract product info from text
│   ├── xlsx_loader.py      # Load reference XLSX files
│   ├── xlsx_writer.py      # Generate XLSX output
│   ├── comparator.py       # Compare extracted vs reference
│   ├── learner.py          # Learning feedback loop
│   └── reporter.py         # Generate reports
├── input/
│   ├── learning/           # IDML + XLSX pairs for learning
│   └── processing/         # IDML files to process
├── output/
│   ├── xlsx/               # Generated XLSX files
│   └── reports/            # Validation reports
├── scripts/
│   ├── run_learning.sh/.bat
│   ├── run_process.sh/.bat
│   └── run_check.sh/.bat
├── tests/                  # Unit tests
├── requirements.txt        # Python dependencies
├── .gitignore
└── README.md
```

## Key Metrics

| Metric | Description |
|--------|-------------|
| Accuracy | Match rate between extracted and reference values |
| Matches | Fields with correct values |
| Mismatches | Fields with incorrect values |
| New Fields | Fields in IDML not in XLSX schema |
| Missing | Expected fields not found in IDML |

## Commands Reference

| Command | Purpose |
|---------|---------|
| `learn` | Learn patterns from learning folder pairs |
| `process` | Process IDML files to XLSX |
| `check` | Validate all files and generate reports |
| `validate` | Validate a single IDML/XLSX pair |
| `stats` | Show aggregate learning statistics |
| `list-reports` | List generated reports |
| `clean-reports` | Remove old reports |
| `info` | Show project information |

## Contributing

1. Fork the repository
2. Create a feature branch
3. Add tests for new functionality
4. Submit a pull request

## License

MIT License - See LICENSE file for details.

## Support

For issues and feature requests, please use the GitHub Issues page.

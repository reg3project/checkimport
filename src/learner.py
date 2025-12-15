"""
Learner - Positive Learning Feedback Loop

This module implements the learning system that:
1. Learns patterns from manually created XLSX reference files
2. Applies learned patterns to improve extraction accuracy
3. Tracks learning progress over time
4. Suggests improvements based on mismatches

The feedback loop:
┌─────────────────────────────────────────────────────────────────┐
│  LEARNING DATA (input/learning/)                                │
│  ┌──────────┐     ┌──────────┐                                  │
│  │  IDML    │ ──> │  XLSX    │  (manually created reference)    │
│  └──────────┘     └──────────┘                                  │
└─────────────────────────────────────────────────────────────────┘
           │                │
           ▼                ▼
    ┌──────────────────────────────────────┐
    │     LEARN PATTERNS                   │
    │  - Attribute name mappings           │
    │  - Value transformations             │
    │  - Style-to-field associations       │
    │  - Table structure patterns          │
    └──────────────────────────────────────┘
           │
           ▼
    ┌──────────────────────────────────────┐
    │     KNOWLEDGE BASE                   │
    │  (learning_data.json)                │
    └──────────────────────────────────────┘
           │
           ▼
┌─────────────────────────────────────────────────────────────────┐
│  PROCESSING DATA (input/processing/)                            │
│  ┌──────────┐                                                   │
│  │  IDML    │ ──> Apply patterns ──> Generate XLSX              │
│  └──────────┘                                                   │
└─────────────────────────────────────────────────────────────────┘
           │
           ▼
    ┌──────────────────────────────────────┐
    │     VALIDATE & IMPROVE               │
    │  - Compare with expectations         │
    │  - Identify new patterns             │
    │  - Update knowledge base             │
    └──────────────────────────────────────┘
"""

import json
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple, Set
from dataclasses import dataclass, field, asdict
from datetime import datetime
from collections import defaultdict
import re
import logging

from .comparator import ComparisonResult, FieldComparison
from .xlsx_loader import XLSXData, load_xlsx
from .idml_parser import IDMLDocument, parse_idml

logger = logging.getLogger(__name__)


@dataclass
class AttributeMapping:
    """Mapping from raw attribute name to standard field"""
    raw_name: str
    standard_name: str
    confidence: float = 1.0
    examples: List[str] = field(default_factory=list)
    source_count: int = 1


@dataclass
class ValueTransform:
    """Transformation rule for values"""
    field_name: str
    pattern: str  # Regex pattern
    replacement: str
    description: str = ""


@dataclass
class StyleMapping:
    """Mapping from style name to field type"""
    style_pattern: str
    field_type: str  # 'title', 'description', 'badge', etc.
    confidence: float = 1.0


@dataclass
class LearningData:
    """Knowledge base from learning"""
    version: str = "1.0"
    last_updated: str = ""
    files_learned: int = 0
    attribute_mappings: Dict[str, AttributeMapping] = field(default_factory=dict)
    value_transforms: List[ValueTransform] = field(default_factory=list)
    style_mappings: List[StyleMapping] = field(default_factory=list)
    field_patterns: Dict[str, List[str]] = field(default_factory=dict)
    accuracy_history: List[Dict[str, Any]] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to serializable dictionary"""
        return {
            'version': self.version,
            'last_updated': self.last_updated,
            'files_learned': self.files_learned,
            'attribute_mappings': {
                k: asdict(v) for k, v in self.attribute_mappings.items()
            },
            'value_transforms': [asdict(v) for v in self.value_transforms],
            'style_mappings': [asdict(s) for s in self.style_mappings],
            'field_patterns': self.field_patterns,
            'accuracy_history': self.accuracy_history
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'LearningData':
        """Create from dictionary"""
        ld = cls()
        ld.version = data.get('version', '1.0')
        ld.last_updated = data.get('last_updated', '')
        ld.files_learned = data.get('files_learned', 0)

        for k, v in data.get('attribute_mappings', {}).items():
            ld.attribute_mappings[k] = AttributeMapping(**v)

        for v in data.get('value_transforms', []):
            ld.value_transforms.append(ValueTransform(**v))

        for s in data.get('style_mappings', []):
            ld.style_mappings.append(StyleMapping(**s))

        ld.field_patterns = data.get('field_patterns', {})
        ld.accuracy_history = data.get('accuracy_history', [])

        return ld


class Learner:
    """Learning system for improving extraction accuracy"""

    KNOWLEDGE_FILE = "learning_data.json"

    def __init__(self, learning_dir: Path, output_dir: Path):
        self.learning_dir = Path(learning_dir)
        self.output_dir = Path(output_dir)
        self.knowledge_path = output_dir / self.KNOWLEDGE_FILE
        self.knowledge = self._load_knowledge()

    def _load_knowledge(self) -> LearningData:
        """Load existing knowledge base"""
        if self.knowledge_path.exists():
            try:
                with open(self.knowledge_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                return LearningData.from_dict(data)
            except Exception as e:
                logger.warning(f"Could not load knowledge base: {e}")
        return LearningData()

    def _save_knowledge(self):
        """Save knowledge base"""
        self.knowledge.last_updated = datetime.now().isoformat()
        self.output_dir.mkdir(parents=True, exist_ok=True)

        with open(self.knowledge_path, 'w', encoding='utf-8') as f:
            json.dump(self.knowledge.to_dict(), f, indent=2)

        logger.info(f"Saved knowledge base to: {self.knowledge_path}")

    def learn_from_pairs(self) -> Dict[str, Any]:
        """Learn from all IDML/XLSX pairs in learning directory"""
        pairs = self._find_learning_pairs()

        if not pairs:
            return {'error': 'No learning pairs found', 'pairs_found': 0}

        results = {
            'pairs_processed': 0,
            'patterns_learned': 0,
            'accuracy_before': self._get_current_accuracy(),
            'accuracy_after': 0.0,
            'new_mappings': [],
            'details': []
        }

        for idml_path, xlsx_path in pairs:
            try:
                pair_result = self._learn_from_pair(idml_path, xlsx_path)
                results['details'].append(pair_result)
                results['pairs_processed'] += 1
                results['patterns_learned'] += pair_result.get('new_patterns', 0)
            except Exception as e:
                logger.error(f"Error learning from {idml_path.name}: {e}")
                results['details'].append({
                    'file': idml_path.name,
                    'error': str(e)
                })

        # Update knowledge base
        self.knowledge.files_learned = results['pairs_processed']
        self._save_knowledge()

        # Record accuracy
        results['accuracy_after'] = self._calculate_accuracy(pairs)
        self._record_accuracy(results['accuracy_after'])

        return results

    def _find_learning_pairs(self) -> List[Tuple[Path, Path]]:
        """Find matching IDML/XLSX pairs in learning directory"""
        pairs = []

        idml_files = list(self.learning_dir.glob("*.idml"))

        for idml_path in idml_files:
            # Look for matching XLSX
            xlsx_name = idml_path.stem + ".xlsx"
            xlsx_path = self.learning_dir / xlsx_name

            if xlsx_path.exists():
                pairs.append((idml_path, xlsx_path))
            else:
                # Try case-insensitive match
                for xlsx_file in self.learning_dir.glob("*.xlsx"):
                    if xlsx_file.stem.lower() == idml_path.stem.lower():
                        pairs.append((idml_path, xlsx_file))
                        break

        return pairs

    def _learn_from_pair(self, idml_path: Path, xlsx_path: Path) -> Dict[str, Any]:
        """Learn patterns from a single IDML/XLSX pair"""
        result = {
            'file': idml_path.name,
            'new_patterns': 0,
            'attribute_mappings': [],
            'value_patterns': []
        }

        # Parse IDML
        document = parse_idml(idml_path)

        # Load reference XLSX
        reference = load_xlsx(xlsx_path)

        # Learn attribute mappings from tables
        mappings = self._learn_attribute_mappings(document, reference)
        for mapping in mappings:
            if mapping.raw_name not in self.knowledge.attribute_mappings:
                self.knowledge.attribute_mappings[mapping.raw_name] = mapping
                result['new_patterns'] += 1
                result['attribute_mappings'].append(mapping.raw_name)

        # Learn value patterns
        patterns = self._learn_value_patterns(document, reference)
        for field_name, pattern_list in patterns.items():
            if field_name not in self.knowledge.field_patterns:
                self.knowledge.field_patterns[field_name] = pattern_list
                result['new_patterns'] += len(pattern_list)
                result['value_patterns'].extend(pattern_list)

        return result

    def _learn_attribute_mappings(
        self,
        document: IDMLDocument,
        reference: XLSXData
    ) -> List[AttributeMapping]:
        """Learn attribute name mappings"""
        mappings = []

        # Extract all attribute names from IDML tables
        idml_attributes = set()
        for table in document.tables:
            for row in range(table.rows):
                cell = table.get_cell(row, 0)
                if cell and cell.content:
                    idml_attributes.add(cell.content.strip().lower())

        # Get all field names from reference XLSX
        xlsx_fields = set(reference.prodotti_columns + reference.sku_columns)

        # Find potential mappings
        for idml_attr in idml_attributes:
            for xlsx_field in xlsx_fields:
                if self._attributes_match(idml_attr, xlsx_field):
                    mapping = AttributeMapping(
                        raw_name=idml_attr,
                        standard_name=xlsx_field,
                        confidence=self._calculate_mapping_confidence(idml_attr, xlsx_field)
                    )
                    mappings.append(mapping)

        return mappings

    def _attributes_match(self, idml_attr: str, xlsx_field: str) -> bool:
        """Check if an IDML attribute matches an XLSX field"""
        # Normalize both
        idml_norm = re.sub(r'[^a-z0-9]', '', idml_attr.lower())
        xlsx_norm = re.sub(r'[^a-z0-9]', '', xlsx_field.lower())

        # Direct match
        if idml_norm == xlsx_norm:
            return True

        # Substring match
        if idml_norm in xlsx_norm or xlsx_norm in idml_norm:
            return True

        # Common translations (IT -> EN)
        translations = {
            'tensione': 'voltage',
            'alimentazione': 'power',
            'peso': 'weight',
            'dimensioni': 'dimensions',
            'motore': 'motor',
            'velocita': 'speed',
            'coppia': 'torque',
            'temperatura': 'temperature',
            'corrente': 'current',
            'frequenza': 'frequency',
        }

        if idml_norm in translations:
            if translations[idml_norm] in xlsx_norm:
                return True

        return False

    def _calculate_mapping_confidence(self, idml_attr: str, xlsx_field: str) -> float:
        """Calculate confidence score for a mapping"""
        idml_norm = re.sub(r'[^a-z0-9]', '', idml_attr.lower())
        xlsx_norm = re.sub(r'[^a-z0-9]', '', xlsx_field.lower())

        if idml_norm == xlsx_norm:
            return 1.0

        # Calculate similarity
        matches = sum(1 for a, b in zip(idml_norm, xlsx_norm) if a == b)
        max_len = max(len(idml_norm), len(xlsx_norm))

        return matches / max_len if max_len > 0 else 0.0

    def _learn_value_patterns(
        self,
        document: IDMLDocument,
        reference: XLSXData
    ) -> Dict[str, List[str]]:
        """Learn value patterns from reference data"""
        patterns = defaultdict(list)

        # Extract patterns from reference values
        for product in reference.prodotti:
            for field, value in product.items():
                if value:
                    pattern = self._extract_value_pattern(str(value))
                    if pattern and pattern not in patterns[field]:
                        patterns[field].append(pattern)

        for sku in reference.sku:
            for field, value in sku.items():
                if value:
                    pattern = self._extract_value_pattern(str(value))
                    if pattern and pattern not in patterns[field]:
                        patterns[field].append(pattern)

        return dict(patterns)

    def _extract_value_pattern(self, value: str) -> Optional[str]:
        """Extract a generalizable pattern from a value"""
        if not value:
            return None

        # Number with unit
        if re.match(r'^\d+(?:[.,]\d+)?\s*[a-zA-Z]+$', value):
            return r'\d+(?:[.,]\d+)?\s*[a-zA-Z]+'

        # Pure number
        if re.match(r'^\d+(?:[.,]\d+)?$', value):
            return r'\d+(?:[.,]\d+)?'

        # Code pattern
        if re.match(r'^[A-Z]{1,3}\d{4,}$', value):
            return r'[A-Z]{1,3}\d{4,}'

        return None

    def apply_knowledge(self, document: IDMLDocument) -> Dict[str, Any]:
        """Apply learned knowledge to improve extraction"""
        improvements = {
            'attribute_mappings_applied': 0,
            'value_transforms_applied': 0,
            'enhanced_fields': []
        }

        # This would modify the extraction process using learned patterns
        # For now, return what knowledge could be applied

        for raw_name, mapping in self.knowledge.attribute_mappings.items():
            if mapping.confidence >= 0.8:
                improvements['attribute_mappings_applied'] += 1
                improvements['enhanced_fields'].append(mapping.standard_name)

        return improvements

    def _get_current_accuracy(self) -> float:
        """Get most recent accuracy from history"""
        if self.knowledge.accuracy_history:
            return self.knowledge.accuracy_history[-1].get('accuracy', 0.0)
        return 0.0

    def _calculate_accuracy(self, pairs: List[Tuple[Path, Path]]) -> float:
        """Calculate accuracy across all learning pairs"""
        from .comparator import compare_files

        total_matches = 0
        total_compared = 0

        for idml_path, xlsx_path in pairs:
            try:
                result = compare_files(idml_path, xlsx_path)
                total_matches += len(result.matches)
                total_compared += len(result.matches) + len(result.mismatches)
            except Exception:
                pass

        return (total_matches / total_compared * 100) if total_compared > 0 else 0.0

    def _record_accuracy(self, accuracy: float):
        """Record accuracy measurement"""
        self.knowledge.accuracy_history.append({
            'timestamp': datetime.now().isoformat(),
            'accuracy': accuracy,
            'files_learned': self.knowledge.files_learned
        })

    def get_learning_summary(self) -> Dict[str, Any]:
        """Get summary of learned knowledge"""
        return {
            'files_learned': self.knowledge.files_learned,
            'attribute_mappings': len(self.knowledge.attribute_mappings),
            'value_transforms': len(self.knowledge.value_transforms),
            'style_mappings': len(self.knowledge.style_mappings),
            'field_patterns': len(self.knowledge.field_patterns),
            'accuracy_history': self.knowledge.accuracy_history[-10:],  # Last 10
            'last_updated': self.knowledge.last_updated
        }

    def suggest_improvements(
        self,
        comparison_results: List[ComparisonResult]
    ) -> List[Dict[str, Any]]:
        """Suggest improvements based on comparison mismatches"""
        suggestions = []

        # Analyze mismatches
        mismatch_fields = defaultdict(list)
        for result in comparison_results:
            for mismatch in result.mismatches:
                mismatch_fields[mismatch.field_name].append({
                    'extracted': mismatch.extracted_value,
                    'expected': mismatch.reference_value
                })

        # Generate suggestions for frequent mismatches
        for field, mismatches in mismatch_fields.items():
            if len(mismatches) >= 2:  # Pattern in multiple files
                suggestion = {
                    'field': field,
                    'mismatch_count': len(mismatches),
                    'suggestion_type': 'mapping',
                    'examples': mismatches[:3],
                    'recommendation': f"Review extraction logic for '{field}' - {len(mismatches)} mismatches found"
                }
                suggestions.append(suggestion)

        return suggestions


def create_learner(learning_dir: Path, output_dir: Path) -> Learner:
    """Create a learner instance"""
    return Learner(learning_dir, output_dir)


def run_learning_cycle(learning_dir: Path, output_dir: Path) -> Dict[str, Any]:
    """Run a complete learning cycle"""
    learner = create_learner(learning_dir, output_dir)
    return learner.learn_from_pairs()

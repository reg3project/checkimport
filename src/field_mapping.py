"""
Field Mapping - Map between Italian XLSX columns and IDML extracted fields

This module provides mappings to translate between:
- Italian XLSX column names (from FAAC reference files)
- Standard English field names
- IDML extracted attribute names
"""

from typing import Dict, List, Optional, Tuple, Any
import re


# ============================================================================
# PRODOTTI SHEET MAPPINGS (Product-level fields)
# ============================================================================

PRODOTTI_MAPPING = {
    # Italian column name -> (English name, extraction hints)
    'categoria_prodotto': ('category', ['categoria', 'category']),
    'nome_prodotto': ('product_name', ['nome', 'name', 'prodotto']),
    'nome_asta': ('bar_name', ['asta', 'bar']),
    'pagina_catalogo': ('catalog_page', ['pagina', 'page']),
    'tipo_layout': ('layout_type', ['layout', 'tipo']),
    'immagine_principale': ('main_image', ['immagine', 'image']),
    'codici_modelli': ('model_codes', ['codici', 'modelli', 'sku']),
    'titolo_prodotto': ('product_title', ['titolo', 'title']),
    'descrizione_prodotto': ('product_description', ['descrizione', 'description']),
    'intensita_transito': ('traffic_intensity', ['transito', 'traffic', 'intensità']),
    'caratteristica_primaria': ('primary_feature_label', ['caratteristica']),
    'valore_primario': ('primary_feature_value', ['valore']),
    'caratteristica_secondaria': ('secondary_feature_label', []),
    'valore_secondario': ('secondary_feature_value', []),
    'caratteristica_terziaria': ('tertiary_feature_label', []),
    'valore_terziario': ('tertiary_feature_value', []),
    'novita': ('is_new', ['novità', 'new', 'nuovo']),
    'veloce': ('is_fast', ['veloce', 'fast', 'rapido']),
    'solare': ('is_solar', ['solare', 'solar']),
    'brevetto_faac': ('faac_patent', ['brevetto', 'patent']),
    'badge_sistemi': ('system_badges', ['badge', 'sistemi', 'icone']),
    'codice_qr': ('qr_code', ['qr', 'code']),
    'certificazioni': ('certifications', ['certificazioni', 'cert', 'ce', 'en']),
    'descrizione_categoria': ('category_description', []),
    'contenuto_confezione': ('package_contents', ['confezione', 'contenuto', 'kit']),
    'schema_installazione': ('installation_schema', ['schema', 'installazione']),
    'immagne_schema': ('schema_image', []),
    'componenti_kit': ('kit_components', ['componenti', 'kit']),
    'immagine_kit': ('kit_image', []),
    'sku_correlati': ('related_skus', ['correlati', 'related']),
    'prodotti_correlati': ('related_products', ['prodotti correlati']),
    'note_prodotto': ('product_notes', ['note']),
    'quote_installazione': ('installation_quotes', ['quote']),
    'grafico_tecnico': ('technical_graph', ['grafico']),
    'tabella_molle': ('springs_table', ['molle', 'tabella']),
    'accessori_disponibili': ('available_accessories', ['accessori']),
}


# ============================================================================
# SKU SHEET MAPPINGS (Technical specifications)
# ============================================================================

SKU_MAPPING = {
    # Italian column name -> (English name, IDML attribute patterns)
    'SKU': ('sku', ['sku', 'codice', 'code']),
    'COUNTIF': ('count', []),
    'SKU Immagine': ('sku_image', ['immagine']),
    'Tipo': ('type', ['tipo']),
    'Nome Modello': ('model_name', ['modello', 'model']),
    'Modelli Correlati': ('related_models', ['correlati']),
    'Descrizione Breve': ('short_description', ['descrizione']),
    'Confezione': ('package', ['confezione']),

    # Electrical specs
    'Tensione di alimentazione di rete': ('supply_voltage', ['tensione', 'alimentazione', 'voltage']),
    'Corrente assorbita': ('absorbed_current', ['corrente', 'current']),
    'Motore elettrico': ('electric_motor', ['motore', 'motor']),
    'Potenza max': ('max_power', ['potenza', 'power', 'watt']),
    'Coppia max': ('max_torque', ['coppia', 'torque']),

    # Mechanical specs
    'Tipo di materiale': ('material_type', ['materiale', 'material']),
    'Tipo di trattamento': ('treatment_type', ['trattamento']),
    'Forza max di spinta': ('max_thrust_force', ['forza', 'spinta', 'force']),
    'Rapporto di riduzione': ('reduction_ratio', ['rapporto', 'riduzione']),
    'Velocità angolare max': ('max_angular_speed', ['velocità angolare']),
    "Velocità dell'anta": ('leaf_speed', ['velocità anta']),
    'Velocità max stelo': ('max_stem_speed', ['velocità stelo', 'velocità max']),

    # Dimensions
    'Lunghezza max anta': ('max_leaf_length', ['lunghezza anta']),
    'Lunghezza max asta': ('max_bar_length', ['lunghezza asta']),
    'Larghezza max anta': ('max_leaf_width', ['larghezza']),
    'Peso max anta': ('max_leaf_weight', ['peso anta', 'peso max']),
    'Peso': ('weight', ['peso']),
    'Dimensioni (LxPxH)': ('dimensions_lxwxh', ['dimensioni', 'dimension']),

    # Movement specs
    'Corsa dello stelo': ('stem_stroke', ['corsa', 'stroke']),
    'Angolo max apertura anta': ('max_opening_angle', ['angolo', 'apertura']),
    'Spazio di fermata': ('stopping_space', ['fermata']),
    'Tempo di apertura': ('opening_time', ['tempo apertura']),

    # Control
    'Regolazione velocità e controllo motore': ('speed_regulation', ['regolazione velocità']),
    'Finecorsa': ('limit_switch', ['finecorsa']),
    'Pignone': ('pinion', ['pignone']),
    'Regolazione della forza': ('force_regulation', ['regolazione forza']),

    # Environmental
    'Temperatura ambiente di esercizio': ('operating_temperature', ['temperatura']),
    'Termoprotezione': ('thermal_protection', ['termoprotezione', 'thermal']),
    'Grado di protezione': ('protection_rating', ['grado protezione', 'ip']),

    # Usage
    'Frequenza di utilizzo': ('usage_frequency', ['frequenza', 'cicli']),
    'Tempo di utilizzo continuo (ROT)': ('continuous_use_time', ['utilizzo continuo']),

    # Other
    'Apparecchiatura elettronica': ('electronic_equipment', ['apparecchiatura', 'scheda']),
    'Arresti meccanici integrati in apertura e chiusura': ('integrated_stops', ['arresti']),
    'Encoder': ('encoder', ['encoder']),
    'Tipo di rallentamento': ('deceleration_type', ['rallentamento']),
    'Tipo di asta': ('bar_type', ['tipo asta']),
    'Dispositivo di sblocco': ('unlock_device', ['sblocco']),
    'Condensatore di spunto': ('starting_capacitor', ['condensatore']),

    # Hydraulic
    'Portata gruppo motore-pompa': ('pump_flow_rate', ['portata', 'pompa']),
    'Tipo di olio': ('oil_type', ['olio', 'oil']),
    'Staffe di fissaggio': ('mounting_brackets', ['staffe', 'fissaggio']),
}


# ============================================================================
# IDML ATTRIBUTE TO XLSX COLUMN MAPPING
# ============================================================================

def normalize_attribute(attr: str) -> str:
    """Normalize an attribute name for matching"""
    # Lowercase
    result = attr.lower().strip()
    # Remove special characters except spaces
    result = re.sub(r'[^\w\s]', '', result)
    # Normalize whitespace
    result = re.sub(r'\s+', ' ', result)
    return result


def find_xlsx_column_for_idml_attr(idml_attr: str) -> Optional[str]:
    """Find the XLSX column name that matches an IDML attribute"""
    normalized = normalize_attribute(idml_attr)

    # Check SKU mappings first (more specific)
    for xlsx_col, (eng_name, patterns) in SKU_MAPPING.items():
        xlsx_normalized = normalize_attribute(xlsx_col)

        # Exact match
        if normalized == xlsx_normalized:
            return xlsx_col

        # Pattern match
        for pattern in patterns:
            if pattern.lower() in normalized or normalized in pattern.lower():
                return xlsx_col

    # Check prodotti mappings
    for xlsx_col, (eng_name, patterns) in PRODOTTI_MAPPING.items():
        xlsx_normalized = normalize_attribute(xlsx_col)

        if normalized == xlsx_normalized:
            return xlsx_col

        for pattern in patterns:
            if pattern.lower() in normalized or normalized in pattern.lower():
                return xlsx_col

    return None


def get_english_name(xlsx_col: str) -> str:
    """Get the English field name for an XLSX column"""
    if xlsx_col in SKU_MAPPING:
        return SKU_MAPPING[xlsx_col][0]
    if xlsx_col in PRODOTTI_MAPPING:
        return PRODOTTI_MAPPING[xlsx_col][0]
    return xlsx_col.lower().replace(' ', '_')


def get_all_xlsx_columns() -> Tuple[List[str], List[str]]:
    """Get all XLSX column names"""
    prodotti_cols = list(PRODOTTI_MAPPING.keys())
    sku_cols = list(SKU_MAPPING.keys())
    return prodotti_cols, sku_cols


# ============================================================================
# ENGLISH TO ITALIAN REVERSE MAPPING
# ============================================================================

# Maps English field names (from ProductInfo.to_dict) to Italian XLSX columns
ENGLISH_TO_ITALIAN_PRODUCT = {
    'name': 'nome_prodotto',
    'category': 'categoria_prodotto',
    'subcategory': 'subcategoria',
    'page': 'pagina_catalogo',
    'description': 'descrizione_prodotto',
    'short_description': 'descrizione_breve',
    'features': 'caratteristiche',
    'badges': 'badge_sistemi',
    'certifications': 'certificazioni',
    'accessories': 'accessori_disponibili',
    'images': 'immagine_principale',
    'sku_codes': 'codici_modelli',
    'componenti_kit': 'componenti_kit',
    'sku_correlati': 'sku_correlati',
    # Direct Italian mappings
    'tipo_layout': 'tipo_layout',
    'pagina_catalogo': 'pagina_catalogo',
    'titolo_prodotto': 'titolo_prodotto',
    'descrizione_categoria': 'descrizione_categoria',
    'caratteristica_primaria': 'caratteristica_primaria',
    'valore_primario': 'valore_primario',
    'caratteristica_secondaria': 'caratteristica_secondaria',
    'valore_secondario': 'valore_secondario',
    'intensita_transito': 'intensita_transito',
    'codici_modelli': 'codici_modelli',
}

# Maps English field names to Italian XLSX columns for SKU
ENGLISH_TO_ITALIAN_SKU = {
    'sku': 'SKU',
    'model_name': 'Nome Modello',
    'supply_voltage': 'Tensione di alimentazione di rete',
    'absorbed_current': 'Corrente assorbita',
    'electric_motor': 'Motore elettrico',
    'max_power': 'Potenza max',
    'max_torque': 'Coppia max',
    'max_thrust_force': 'Forza max di spinta',
    'max_stem_speed': 'Velocità max stelo',
    'max_angular_speed': 'Velocità angolare max',
    'leaf_speed': "Velocità dell'anta",
    'pump_flow_rate': 'Portata gruppo motore-pompa',
    'stem_stroke': 'Corsa dello stelo',
    'max_opening_angle': 'Angolo max apertura anta',
    'operating_temperature': 'Temperatura ambiente di esercizio',
    'thermal_protection': 'Termoprotezione',
    'protection_rating': 'Grado di protezione',
    'weight': 'Peso',
    'usage_frequency': 'Frequenza di utilizzo',
    'max_leaf_width': 'Larghezza max anta',
    'max_leaf_length': 'Lunghezza max anta',
    'max_leaf_weight': 'Peso max anta',
    'oil_type': 'Tipo di olio',
    'mounting_brackets': 'Staffe di fissaggio',
    'dimensions_lxwxh': 'Dimensioni (LxPxH)',
    'electronic_equipment': 'Apparecchiatura elettronica',
    'unlock_device': 'Dispositivo di sblocco',
    'limit_switch': 'Finecorsa',
    'encoder': 'Encoder',
}


def get_italian_column_for_english(english_name: str) -> Optional[str]:
    """Get Italian XLSX column name for English field name"""
    if english_name in ENGLISH_TO_ITALIAN_PRODUCT:
        return ENGLISH_TO_ITALIAN_PRODUCT[english_name]
    if english_name in ENGLISH_TO_ITALIAN_SKU:
        return ENGLISH_TO_ITALIAN_SKU[english_name]
    return None


def convert_product_dict_to_italian(product_dict: Dict[str, Any]) -> Dict[str, Any]:
    """Convert ProductInfo.to_dict() keys from English to Italian"""
    result = {}
    for eng_key, value in product_dict.items():
        ita_key = ENGLISH_TO_ITALIAN_PRODUCT.get(eng_key, eng_key)
        result[ita_key] = value
    return result


# ============================================================================
# IDML EXTRACTION TO DATA.XLSX COLUMN MAPPING
# ============================================================================

# Maps IDML extracted field names -> Data.xlsx column names (snake_case)
IDML_TO_DATA_XLSX = {
    # Technical specs
    'Tensione di alimentazione di rete': 'tensione_alimentazione',
    'Corrente assorbita': 'corrente_assorbita',
    'Motore elettrico': 'tipo_motore',
    'Potenza max': 'potenza_massima',
    'Coppia max': 'coppia_massima',
    'Forza max di spinta': 'forza_spinta',
    'Velocità max stelo': 'velocita_stelo',
    'Velocità angolare max': 'velocita_angolare',
    "Velocità dell'anta": 'velocita_anta',
    'Portata gruppo motore-pompa': 'portata_pompa',
    'Corsa dello stelo': 'corsa_stelo',
    'Angolo max apertura anta': 'angolo_apertura_max',
    'Temperatura ambiente di esercizio': 'temperatura_esercizio',
    'Termoprotezione': 'termoprotezione',
    'Grado di protezione': 'grado_protezione_ip',
    'Peso': 'peso_unita',
    'Dimensioni (LxPxH)': 'dimensioni',
    'Frequenza di utilizzo': 'frequenza_utilizzo',
    'Larghezza max anta': 'larghezza_anta_max',
    'Lunghezza max anta': 'lunghezza_max',
    'Peso max anta': 'peso_anta_max',
    'Tipo di olio': 'tipo_olio',
    'Staffe di fissaggio': 'staffe_fissaggio',
    'Apparecchiatura elettronica': 'scheda_elettronica',
    'Dispositivo di sblocco': 'dispositivo_sblocco',
    'Finecorsa': 'finecorsa',
    'Encoder': 'encoder',
    'Tipo di materiale': 'materiale',
    'Tipo di trattamento': 'trattamento',
    'Tipo di rallentamento': 'tipo_rallentamento',
    'Tipo di asta': 'tipo_asta',
    'Condensatore di spunto': 'condensatore_spunto',
    'Pignone': 'pignone',
    'Nome Modello': 'nome_modello',
    # Reverse mapping for comparison
    'tensione_alimentazione': 'Tensione di alimentazione di rete',
    'tipo_motore': 'Motore elettrico',
    'potenza_massima': 'Potenza max',
    'coppia_massima': 'Coppia max',
    'forza_spinta': 'Forza max di spinta',
    'grado_protezione_ip': 'Grado di protezione',
    'peso_unita': 'Peso',
    'larghezza_anta_max': 'Larghezza max anta',
    'angolo_apertura_max': 'Angolo max apertura anta',
    'scheda_elettronica': 'Apparecchiatura elettronica',
}


def get_data_xlsx_column(idml_field: str) -> str:
    """Convert IDML field name to Data.xlsx column name"""
    return IDML_TO_DATA_XLSX.get(idml_field, idml_field)


def get_idml_field_from_data_xlsx(data_col: str) -> str:
    """Convert Data.xlsx column name to IDML field name"""
    # Check reverse mapping
    for idml, data in IDML_TO_DATA_XLSX.items():
        if data == data_col:
            return idml
    return data_col


# ============================================================================
# VALUE NORMALIZATION
# ============================================================================

def normalize_value(value: str) -> str:
    """Normalize a value for comparison"""
    if not value:
        return ""

    result = str(value).strip()

    # Normalize whitespace
    result = re.sub(r'\s+', ' ', result)

    # Normalize decimal separators (Italian uses comma)
    # But be careful not to change things like "1,5 lpm"

    # Remove trailing/leading quotes
    result = result.strip('"\'')

    return result


def extract_numeric(value: str) -> Optional[float]:
    """Extract numeric value from string"""
    if not value:
        return None

    # Find first number pattern (with comma or period as decimal)
    match = re.search(r'[\d]+[,.]?[\d]*', value.replace(',', '.'))
    if match:
        try:
            return float(match.group())
        except ValueError:
            pass
    return None


def values_match(val1: str, val2: str, tolerance: float = 0.01) -> bool:
    """Check if two values match (with numeric tolerance)"""
    v1 = normalize_value(val1)
    v2 = normalize_value(val2)

    # Exact match
    if v1 == v2:
        return True

    # Empty check
    if not v1 or not v2:
        return False

    # Try numeric comparison
    num1 = extract_numeric(v1)
    num2 = extract_numeric(v2)

    if num1 is not None and num2 is not None:
        if num2 != 0:
            rel_diff = abs(num1 - num2) / abs(num2)
            if rel_diff <= tolerance:
                return True
        elif abs(num1 - num2) <= tolerance:
            return True

    # Substring match (one contains the other)
    if v1 in v2 or v2 in v1:
        return True

    return False

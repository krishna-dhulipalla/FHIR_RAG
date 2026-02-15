from typing import Tuple, Optional

def normalize_unit(value: str, unit: str) -> Tuple[str, str]:
    """
    Normalizes values and units to a canonical format.
    Example: 
      - "13.5", "g/dL" -> "13.5", "g/dL" (no change)
      - "135", "g/L"   -> "13.5", "g/dL"
      - "98.6", "degF" -> "37.0", "Cel"
    """
    if not unit or not value:
        return value, unit
    
    try:
        val_float = float(value)
    except ValueError:
        return value, unit

    # Canonical: Hemoglobin in g/dL
    if unit in ["g/L", "gram/liter"]:
        return str(val_float / 10.0), "g/dL"
    
    # Canonical: Temperature in Celsius
    if unit in ["degF", "F", "Fahrenheit"]:
        celsius = (val_float - 32) * 5.0 / 9.0
        return f"{celsius:.1f}", "Cel"

    # Canonical: Glucose in mg/dL (convert mmol/L to mg/dL for glucose is approx * 18)
    # This is context dependent, but we'll stick to simple unit conversions for now.
    
    return value, unit

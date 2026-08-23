"""
Fertilizer recommendation service.
Adapted from smart-agriculture-ai/services/fertilizer_service.py
"""

import numpy as np

SOIL_DICT = {"Sandy": 0, "Loamy": 1, "Black": 2, "Red": 3, "Clayey": 4}
CROP_DICT = {"Wheat": 0, "Rice": 1, "Maize": 2, "Sugarcane": 3, "Cotton": 4}


def get_fertilizer_recommendation(
    model, temperature, humidity, moisture,
    soil_type: str, crop_type: str,
    n, p, k, land_area
) -> dict:
    """
    Returns fertilizer name, computed quantity per acre, total quantity,
    and agronomic explanation.
    """
    soil_type_enc = SOIL_DICT.get(soil_type, 0)
    crop_type_enc = CROP_DICT.get(crop_type, 0)

    input_data = np.array([[
        temperature, humidity, moisture,
        soil_type_enc, crop_type_enc, n, k, p
    ]])
    prediction = model.predict(input_data)[0]

    raw_pred = str(prediction).strip().upper()
    fertilizer_name = raw_pred
    explanation = ""
    base_qty_per_acre = 50

    # Map raw model output to real-world fertilizer names
    if "28" in raw_pred or "28-28" in raw_pred:
        fertilizer_name = "NPK 28-28-0"
    elif "14" in raw_pred:
        fertilizer_name = "NPK 14-35-14"
    elif "10" in raw_pred:
        fertilizer_name = "NPK 10-26-26"
    elif "UREA" in raw_pred:
        fertilizer_name = "Urea (46-0-0)"
    elif "DAP" in raw_pred:
        fertilizer_name = "DAP (18-46-0)"

    # NPK-based heuristic overrides
    if n < 30 and k > 50 and p > 50:
        fertilizer_name = "Urea (46-0-0)"
        explanation = (
            "Nitrogen is critically low while Potassium and Phosphorus are sufficient. "
            "Urea is recommended to rapidly increase leaf and stem growth."
        )
        base_qty_per_acre = 75
    elif p < 30 and n > 40:
        fertilizer_name = "DAP (18-46-0)"
        explanation = (
            "Phosphorus is low, which is vital for root development. "
            "DAP provides a concentrated dose of Phosphorus."
        )
        base_qty_per_acre = 100
    elif k < 30:
        fertilizer_name = "MOP (Muriate of Potash 0-0-60)"
        explanation = (
            "Potassium is deficient. MOP is recommended to improve "
            "disease resistance and water retention."
        )
        base_qty_per_acre = 40
    else:
        if "UREA" in fertilizer_name.upper():
            explanation = "Urea is recommended to supply necessary Nitrogen for your crop type."
            base_qty_per_acre = 60
        elif "DAP" in fertilizer_name.upper():
            explanation = "DAP is recommended to balance early-stage root development."
            base_qty_per_acre = 80
        elif "NPK" in fertilizer_name.upper():
            explanation = (
                f"A balanced {fertilizer_name} blend is optimal for even "
                "nutrient distribution across your field."
            )
            base_qty_per_acre = 50

    total_qty = base_qty_per_acre * land_area

    return {
        "fertilizer": fertilizer_name,
        "qtyPerAcre": base_qty_per_acre,
        "totalQty": total_qty,
        "explanation": explanation,
    }


def get_soil_types() -> list:
    """Return available soil types."""
    return list(SOIL_DICT.keys())


def get_crop_types() -> list:
    """Return available crop types for fertilizer model."""
    return list(CROP_DICT.keys())

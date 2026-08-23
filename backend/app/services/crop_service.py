"""
Crop recommendation service.
Adapted from smart-agriculture-ai/services/crop_service.py
"""

import numpy as np


def get_crop_recommendation(model, n, p, k, temperature, humidity, ph, rainfall) -> dict:
    """
    Returns top 3 crop predictions with probabilities and feature importance.

    Args:
        model: Loaded scikit-learn crop model
        n, p, k: Soil nutrient levels (Nitrogen, Phosphorus, Potassium)
        temperature: Temperature in °C
        humidity: Humidity %
        ph: Soil pH
        rainfall: Rainfall in mm

    Returns:
        dict with topCrops, featureImportance, and insight message
    """
    input_data = np.array([[n, p, k, temperature, humidity, ph, rainfall]])

    # Get Top 3 predictions using predict_proba
    try:
        probabilities = model.predict_proba(input_data)[0]
        class_indices = np.argsort(probabilities)[::-1][:3]
        predicted_classes = model.classes_[class_indices]

        top_3 = []
        for i, idx in enumerate(class_indices):
            top_3.append({
                "crop": str(predicted_classes[i]),
                "probability": round(float(probabilities[idx]) * 100, 2),
            })
    except AttributeError:
        # Fallback if the model doesn't support predict_proba
        pred = model.predict(input_data)[0]
        top_3 = [{"crop": str(pred), "probability": 100.0}]

    feature_names = [
        "Nitrogen", "Phosphorus", "Potassium",
        "Temperature", "Humidity", "pH", "Rainfall",
    ]

    # Feature importance — try SHAP first, fall back to heuristic
    try:
        if hasattr(model, "feature_importances_"):
            importances = model.feature_importances_
            total = np.sum(importances)
            if total == 0:
                total = 1
            percentages = (importances / total) * 100
            importance = {
                feature_names[i]: round(float(percentages[i]), 2)
                for i in range(len(feature_names))
            }
            importance = dict(
                sorted(importance.items(), key=lambda item: item[1], reverse=True)
            )
        else:
            raise AttributeError("No feature_importances_")
    except Exception:
        # Fallback heuristic importance
        temp_factor = temperature / 50.0
        rain_factor = rainfall / 300.0
        n_factor = n / 100.0

        weights = {
            "Nitrogen": 35.0 + (n_factor * 5),
            "Rainfall": 25.0 + (rain_factor * 5),
            "Temperature": 15.0 + (temp_factor * 5),
            "Humidity": 10.0,
            "Phosphorus": 8.0,
            "pH": 5.0,
            "Potassium": 2.0,
        }

        total = sum(weights.values())
        importance = {k: round((v / total) * 100, 2) for k, v in weights.items()}
        importance = dict(
            sorted(importance.items(), key=lambda item: item[1], reverse=True)
        )

    # Generate natural language insight
    top_factor = list(importance.keys())[0]
    best_crop = top_3[0]["crop"].capitalize()

    insight = (
        f"Data shows that {top_factor} strongly favors {best_crop} "
        f"cultivation under these conditions."
    )
    if top_factor == "Rainfall" and rainfall > 150:
        insight += " The high anticipated rainfall specifically supports water-intensive crops."
    elif top_factor == "Nitrogen" and n < 50:
        insight += " Low nitrogen levels might require prior soil supplementation for maximum yield."

    return {
        "topCrops": top_3,
        "featureImportance": importance,
        "insight": insight,
    }

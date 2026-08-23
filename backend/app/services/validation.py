"""
Input validation and clipping utilities.
Adapted from smart-agriculture-ai/utils/validation.py
"""


def validate_and_clip_crop_inputs(n, p, k, ph, temperature, humidity, rainfall):
    """
    Validates crop recommendation inputs. Clips out-of-bounds values
    to realistic defaults and returns warnings.
    """
    warnings = []

    if temperature < 5:
        warnings.append(f"Temperature ({temperature}°C) is unusually low. Adjusted to 5°C.")
        temperature = 5
    elif temperature > 50:
        warnings.append(f"Temperature ({temperature}°C) is unusually high. Adjusted to 50°C.")
        temperature = 50

    if humidity < 10:
        warnings.append(f"Humidity ({humidity}%) is unusually low. Adjusted to 10%.")
        humidity = 10
    elif humidity > 100:
        warnings.append(f"Humidity ({humidity}%) is invalid. Adjusted to 100%.")
        humidity = 100

    if rainfall < 0:
        warnings.append(f"Rainfall ({rainfall}mm) cannot be negative. Adjusted to 0mm.")
        rainfall = 0

    if ph < 3:
        warnings.append(f"Soil pH ({ph}) is too acidic. Adjusted to 3.")
        ph = 3
    elif ph > 10:
        warnings.append(f"Soil pH ({ph}) is too alkaline. Adjusted to 10.")
        ph = 10

    if n < 0:
        n = 0
    if p < 0:
        p = 0
    if k < 0:
        k = 0

    return temperature, humidity, rainfall, ph, n, p, k, warnings


def validate_and_clip_fertilizer_inputs(n, p, k, temperature, humidity, moisture, land_area):
    """Clips fertilizer recommendation inputs to valid ranges."""
    warnings = []

    if temperature < 5:
        temperature = 5
    elif temperature > 50:
        temperature = 50

    if humidity < 10:
        humidity = 10
    elif humidity > 100:
        humidity = 100

    if moisture < 0:
        moisture = 0
    elif moisture > 100:
        moisture = 100

    if n < 0:
        n = 0
    if p < 0:
        p = 0
    if k < 0:
        k = 0

    if land_area <= 0:
        warnings.append("Land area must be greater than 0. Defaulting to 1.")
        land_area = 1.0

    return temperature, humidity, moisture, n, p, k, land_area, warnings

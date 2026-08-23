"""
Plant disease detection service.
Adapted from smart-agriculture-ai/services/disease_service.py
"""

import numpy as np


# Disease class labels — must match training order exactly
DISEASE_CLASSES = [
    "Pepper Bell Bacterial Spot",
    "Pepper Bell Healthy",
    "Potato Early Blight",
    "Potato Healthy",
    "Potato Late Blight",
    "Tomato Bacterial Spot",
    "Tomato Early Blight",
    "Tomato Healthy",
    "Tomato Late Blight",
    "Tomato Leaf Mold",
    "Tomato Septoria Leaf Spot",
    "Tomato Spider Mites",
    "Tomato Target Spot",
    "Tomato Mosaic Virus",
    "Tomato Yellow Leaf Curl Virus",
]

# Treatment recommendations for each disease
TREATMENT_MAP = {
    "Pepper Bell Bacterial Spot": "Apply copper-based bactericides. Remove infected leaves. Avoid overhead watering. Use disease-free seeds.",
    "Pepper Bell Healthy": "No disease detected. Continue regular care and monitoring.",
    "Potato Early Blight": "Apply chlorothalonil or mancozeb fungicide. Remove lower infected leaves. Ensure proper spacing for air circulation.",
    "Potato Healthy": "No disease detected. Maintain regular watering schedule and monitor for pests.",
    "Potato Late Blight": "URGENT: Apply metalaxyl-based fungicide immediately. Remove and destroy infected plants. Avoid overhead irrigation.",
    "Tomato Bacterial Spot": "Apply copper hydroxide spray. Remove infected plant debris. Use drip irrigation instead of overhead watering.",
    "Tomato Early Blight": "Apply fungicide (chlorothalonil or mancozeb). Mulch around plants. Prune lower branches for air circulation.",
    "Tomato Healthy": "No disease detected. Continue regular care with balanced fertilization.",
    "Tomato Late Blight": "URGENT: Apply metalaxyl or phosphorous acid fungicide. Remove infected plants immediately to prevent spread.",
    "Tomato Leaf Mold": "Improve ventilation in greenhouse. Apply fungicide. Reduce humidity levels. Remove affected leaves.",
    "Tomato Septoria Leaf Spot": "Apply copper-based fungicide. Remove infected leaves from bottom up. Mulch to prevent soil splash.",
    "Tomato Spider Mites": "Apply neem oil or insecticidal soap. Increase humidity. Introduce predatory mites for biological control.",
    "Tomato Target Spot": "Apply chlorothalonil fungicide. Prune for better airflow. Avoid working with wet plants.",
    "Tomato Mosaic Virus": "NO CURE — remove and destroy infected plants. Disinfect tools. Use virus-resistant varieties for replanting.",
    "Tomato Yellow Leaf Curl Virus": "NO CURE — control whitefly vectors with neem oil or yellow sticky traps. Remove infected plants. Use resistant varieties.",
}

CONFIDENCE_THRESHOLD = 0.60


def run_disease_detection(model, preprocessed_image: np.ndarray) -> dict:
    """
    Run prediction on a preprocessed leaf image.

    Args:
        model: Loaded TensorFlow/Keras model
        preprocessed_image: numpy array of shape (1, 224, 224, 3), normalized to [0, 1]

    Returns:
        dict with disease name, confidence, recommended action, and low-confidence flag
    """
    prediction = model.predict(preprocessed_image, verbose=0)[0]
    class_index = np.argmax(prediction)
    confidence = float(prediction[class_index])

    disease = DISEASE_CLASSES[class_index]
    low_confidence = confidence < CONFIDENCE_THRESHOLD

    recommended_action = TREATMENT_MAP.get(disease, "Consult a local agricultural expert for diagnosis.")

    if low_confidence:
        recommended_action = (
            f"Low confidence prediction ({confidence*100:.1f}%). "
            "Please upload a clearer image or consult a local agri-expert for accurate diagnosis. "
            f"Best guess: {disease} — {recommended_action}"
        )

    return {
        "detectedDisease": disease,
        "confidenceScore": round(confidence, 4),
        "lowConfidence": low_confidence,
        "recommendedAction": recommended_action,
    }

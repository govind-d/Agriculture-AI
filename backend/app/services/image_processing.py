"""
Image processing utilities.
Adapted from smart-agriculture-ai/utils/image_processing.py
"""

import numpy as np
from PIL import Image
import io


def is_leaf_image(image_bytes: bytes) -> bool:
    """
    OpenCV heuristic to check if the uploaded image is likely a leaf.
    Looks for green/yellow/brown hues common in plant leaves.
    """
    try:
        import cv2

        np_img = np.frombuffer(image_bytes, np.uint8)
        img = cv2.imdecode(np_img, cv2.IMREAD_COLOR)
        if img is None:
            return False

        hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)

        # Color range for green/yellow/brown hues common in leaves
        lower_bound = np.array([20, 20, 20])
        upper_bound = np.array([100, 255, 255])

        mask = cv2.inRange(hsv, lower_bound, upper_bound)
        ratio = cv2.countNonZero(mask) / (img.shape[0] * img.shape[1])

        return ratio > 0.02  # At least 2% leaf-colored pixels
    except ImportError:
        # If OpenCV not available, skip the check
        return True
    except Exception:
        return False


def preprocess_image(image_bytes: bytes, target_size: tuple = (224, 224)) -> np.ndarray:
    """
    Preprocess image for model prediction.

    Args:
        image_bytes: Raw image bytes
        target_size: Target dimensions (width, height)

    Returns:
        numpy array of shape (1, 224, 224, 3) normalized to [0, 1]
    """
    image = Image.open(io.BytesIO(image_bytes))

    # Convert to RGB if necessary (handles RGBA, grayscale, etc.)
    if image.mode != "RGB":
        image = image.convert("RGB")

    image = image.resize(target_size)
    img_array = np.array(image)
    img_array = img_array / 255.0  # Must match training preprocessing
    img_array = np.expand_dims(img_array, axis=0)

    return img_array

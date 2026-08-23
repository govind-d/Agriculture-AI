"""
Cloudinary image upload service.
"""

import cloudinary
import cloudinary.uploader
from app.core.config import settings


def configure_cloudinary():
    """Configure Cloudinary with credentials."""
    if settings.CLOUDINARY_CLOUD_NAME:
        cloudinary.config(
            cloud_name=settings.CLOUDINARY_CLOUD_NAME,
            api_key=settings.CLOUDINARY_API_KEY,
            api_secret=settings.CLOUDINARY_API_SECRET,
            secure=True,
        )
        return True
    return False


async def upload_image(image_bytes: bytes, folder: str = "disease_detections") -> str:
    """
    Upload an image to Cloudinary and return the secure URL.

    Args:
        image_bytes: Raw image bytes
        folder: Cloudinary folder path

    Returns:
        Secure URL of the uploaded image
    """
    if not configure_cloudinary():
        # In dev without Cloudinary, return a placeholder
        return "https://placeholder.dev/disease-image.jpg"

    try:
        import io

        result = cloudinary.uploader.upload(
            io.BytesIO(image_bytes),
            folder=folder,
            resource_type="image",
            transformation=[
                {"width": 800, "height": 800, "crop": "limit"},
                {"quality": "auto"},
                {"fetch_format": "auto"},
            ],
        )
        return result["secure_url"]
    except Exception as e:
        raise ValueError(f"Image upload failed: {str(e)}")

import io
import numpy as np

from PIL import Image, ImageOps
from pillow_heif import register_heif_opener

register_heif_opener()


def decode_image(image_bytes: bytes) -> np.ndarray:
    with Image.open(io.BytesIO(image_bytes)) as image:
        # Correct orientation using EXIF metadata
        image = ImageOps.exif_transpose(image)

        # Convert all supported inputs to RGB
        image = image.convert("RGB")

        return np.asarray(image, dtype=np.uint8)
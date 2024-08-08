"""
Title: LatexExtractorMixed
Author: Trojan
Date: 27-06-2024
"""
import logging
import os
from typing import Any

from PIL import Image

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')


class LatexExtractorMixed:
    def __init__(self, model: Any):
        self.latex_model_mixed = model
        self.downloaded_file_path = os.path.join("downloaded_images", "verification_image.png")

    def recognize_image(self, request_id: str):
        """Recognize text in the given image and optionally save the result."""
        try:
            image = Image.open(self.downloaded_file_path).convert('RGB')
            latex_mixed_result = self.latex_model_mixed.recognize(image)
            logging.info(f"Request id : {request_id} -> Extracted: {latex_mixed_result}")
        except Exception as e:
            logging.error(f"Request id : {request_id} -> Error with exception: {e}")
            return {"error": str(e)}
        return latex_mixed_result

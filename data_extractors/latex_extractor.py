"""
Title: LatexExtractor
Author: Trojan
Date: 27-06-2024
"""
import os
from typing import Any, Union
import logging


logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')


class LatexExtractor:
    def __init__(self, model: Any):
        self.latex_model = model
        self.downloaded_file_path = os.path.join("downloaded_images", "verification_image.png")

    def convert_image_to_latex(self, request_id: str) -> Union[str, Any]:
        response_object = None

        def process_image(downloaded_image_path):
            try:
                latex_result, latex_elapse = self.latex_model(downloaded_image_path)
                logging.info(f"Request id : {request_id} -> Extracted Text LatexOCR: {latex_result}")
                return latex_result, latex_elapse
            except Exception as e:
                logging.error(f"Request id : {request_id} -> Error with exception: {e}")
                return "Error: Image error!!!", None

        latex_result, latex_elapse = process_image(self.downloaded_file_path)
        logging.info(f"Request id : {request_id} -> latex_result: {latex_result}")

        return latex_result

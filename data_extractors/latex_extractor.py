"""
Title: LatexExtractor
Author: Trojan
Date: 27-06-2024
"""
import os
import requests
from rapid_latex_ocr import LatexOCR
from urllib.parse import urlparse

from data_extractors.utils.response_object_formula import ResponseObjectFormula


class LatexExtractor:
    def __init__(self):
        self.latex_model = LatexOCR()
        self.downloaded_file_path = os.path.join("downloaded_images", "verification_image.png")

    def convert_image_to_latex(self, url: str) -> dict:
        response_object = None

        def process_image(downloaded_image_path):
            try:
                latex_result, latex_elapse = self.latex_model(downloaded_image_path)
                return latex_result, latex_elapse
            except Exception as exc:
                return {"error: Image error!!!"}, None

        parsed_url = urlparse(url)
        if parsed_url.scheme and parsed_url.netloc:
            try:
                response = requests.get(url)
                response.raise_for_status()
                with open(self.downloaded_file_path, 'wb') as f:
                    f.write(response.content)

                latex_result, latex_elapse = process_image(self.downloaded_file_path)
                response_object = ResponseObjectFormula(latex_result, latex_elapse)
            except Exception as e:
                return {"error": str(e)}
        else:
            return {"error": "Invalid URL format"}

        return response_object.to_dict()

"""
Title: AsciimathConverter
Author: Trojan
Date: 27-06-2024
"""

import logging
from typing import Any

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')


class AsciimathConverter:
    def __init__(self, converter_model: Any):
        self.converter_model = converter_model

    def convert_to_ascii(self, request_id: str, latex_expression: str):
        try:
            ascii_result = self.converter_model.translate(latex_expression, from_file=False, pprint=False)
            return ascii_result
        except Exception as e:
            logging.error(f"Request id : {request_id} -> Error: Text is also present in math formula. Can't convert "
                          f"to asciimath.")
            return "Formula with Text. Conversion not available."

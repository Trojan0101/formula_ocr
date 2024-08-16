"""
Title: AsciimathConverter
Author: Trojan
Date: 27-06-2024
"""

import logging
from typing import Any
from pylatexenc.latex2text import LatexNodes2Text


logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')


class AsciimathConverter:
    def __init__(self, converter_model: Any):
        self.converter_model = converter_model

    def convert_to_ascii(self, request_id: str, latex_expression: str):
        ascii_result = []
        try:
            normal_equation = LatexNodes2Text().latex_to_text(latex_expression)
            equations = [eq.replace('?', '').strip() for eq in normal_equation.split('\n') if eq.strip()]
            for i, equation in enumerate(equations, start=1):
                per_ascii_result = ""
                try:
                    per_ascii_result = self.converter_model.translate(equation.strip(), from_file=False, pprint=False)
                except Exception as e:
                    per_ascii_result = "Unrecognized Character"
                per_result_dict = {"type": "asciimath", "value": per_ascii_result}
                ascii_result.append(per_result_dict)
            return ascii_result
        except Exception as e:
            logging.error(f"Request id : {request_id} -> Error: Text is also present in math formula. Can't convert "
                          f"to asciimath.")
            if ascii_result:
                return ascii_result
            else:
                return "Formula with Text. Conversion not available."

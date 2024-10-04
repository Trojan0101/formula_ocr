"""
Title: AsciimathConverter
Author: Trojan
Date: 27-06-2024
"""

import logging
from typing import Any

from py_asciimath.translator.translator import (
    ASCIIMath2MathML,
    ASCIIMath2Tex,
    MathML2Tex,
    Tex2ASCIIMath
)
from pylatexenc.latex2text import LatexNodes2Text


logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')


class AsciimathConverter:
    def __init__(self, converter_model: Any):
        self.converter_model = converter_model

    def convert_to_ascii(self, request_id: str, latex_expression: str):
        ascii_result = []
        try:
            normal_equation = LatexNodes2Text().latex_to_text(latex_expression)
            equations = [eq.replace('?', '').strip().replace('∴', '') for eq in normal_equation.split('\n') if eq.strip()]
            for i, equation in enumerate(equations, start=1):
                per_ascii_result = ""
                try:
                    per_ascii_result = self.converter_model.translate(equation.strip(), from_file=False, pprint=False)
                except Exception as e:
                    break
                per_result_dict = {"type": "asciimath", "value": per_ascii_result}
                ascii_result.append(per_result_dict)
            # Check if all values in ascii_result are "Unrecognized Character"
            ascii_result = []
            try:
                per_ascii_result = self.converter_model.translate(latex_expression.strip(), from_file=False, pprint=False)
            except Exception as e:
                per_ascii_result = "Unrecognized Character"
                return [{"type": "asciimath", "value": per_ascii_result}], normal_equation
            per_result_dict = {"type": "asciimath", "value": per_ascii_result}
            ascii_result.append(per_result_dict)
            return ascii_result, normal_equation
        except Exception as e:
            logging.error(f"E_OCR_005 -> Request id : {request_id} -> Error: Text is also present in math formula. Can't convert "
                          f"to asciimath.")
            if ascii_result:
                return ascii_result, normal_equation
            else:
                return [{"type": "asciimath", "value": "Formula with Text. Conversion not available."}], normal_equation

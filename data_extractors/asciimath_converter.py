"""
Title: Asciimath converter
Author: Trojan
Date: 27-06-2024
"""

import logging
from typing import Any, List, Tuple
from pylatexenc.latex2text import LatexNodes2Text

from utilities.config import LOGGING_LEVEL
from utilities.general_utils import setup_logging

# Logging configuration
setup_logging(LOGGING_LEVEL)


class AsciimathConverter:
    """
    A class to convert LaTeX expressions to AsciiMath using a specified converter model.
    """

    def __init__(self, converter_model: Any):
        """
        Initialize the converter with the given model.

        :param converter_model: The model responsible for translating LaTeX to AsciiMath.
        """
        self.converter_model = converter_model

    def convert_to_ascii(self, request_id: str, latex_expression: str) -> Tuple[List[dict], str]:
        """
        Convert a LaTeX expression into AsciiMath format.

        :param request_id: Unique identifier for the conversion request.
        :param latex_expression: Input LaTeX expression as a string.
        :return: A tuple containing:
                 - List of dictionaries with "type" and "value" keys.
                 - Normalized text representation of the LaTeX expression.
        """
        ascii_result = []
        try:
            normal_equation = LatexNodes2Text().latex_to_text(latex_expression)
            equations = [
                eq.replace('?', '').strip().replace('∴', '')
                for eq in normal_equation.split('\n') if eq.strip()
            ]

            for equation in equations:
                try:
                    per_ascii_result = self.converter_model.translate(
                        equation.strip(), from_file=False, pprint=False
                    )
                except Exception as e:
                    logging.warning(f"Equation conversion failed with error: {str(e)}")
                    per_ascii_result = "Unrecognized Character"

                ascii_result.append({"type": "asciimath", "value": per_ascii_result})

            if not ascii_result or all(res["value"] == "Unrecognized Character" for res in ascii_result):
                try:
                    full_ascii_result = self.converter_model.translate(
                        latex_expression.strip(), from_file=False, pprint=False
                    )
                except Exception as e:
                    logging.error(f"Full expression conversion failed with error: {str(e)}")
                    full_ascii_result = "Unrecognized Character"

                return [{"type": "asciimath", "value": full_ascii_result}], normal_equation

            return ascii_result, normal_equation

        except Exception as e:
            error_dict = {"code": "E_OCR_005", "message": str(e)}
            logging.error(error_dict)
            return [{"type": "asciimath", "value": "Formula with Text. Conversion not available."}], ""

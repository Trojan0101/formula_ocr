"""
Title: API Entry Point
Author: Trojan
Date: 25-06-2024
"""
import logging
import os
import re
from typing import List, Optional

from flask import Flask, request, jsonify
from pix2text import Pix2Text
from py_asciimath.translator.translator import Tex2ASCIIMath

from utilities.config import LOGGING_LEVEL, API_VERSION, DOWNLOADED_IMAGE_PATH
from utilities.core_utils import generate_request_id, parse_request_data, convert_to_ascii, advanced_text_extraction, \
    TEXT, LATEX, construct_response, validate_file, save_file, extract_data_from_image, \
    extract_image_size, parse_form_data
from utilities.general_utils import assign_values_from_request, check_url_and_download_image, setup_logging

# Logging Configuration
setup_logging(LOGGING_LEVEL)

class MyFlaskApp(Flask):
    def __init__(self, import_name):
        super().__init__(import_name)
        self.api_version = API_VERSION

        # Initialize Pix2Text models for different languages
        self.latex_model_english = Pix2Text()
        self.latex_model_korean = self._initialize_latex_model('ko')
        self.latex_model_japanese = self._initialize_latex_model('ja')
        self.latex_model_chinese_sim = self._initialize_latex_model('ch_sim')
        self.latex_model_chinese_tra = self._initialize_latex_model('ch_tra')

        logging.info("Math OCR Models Initialized!!!")

        # Initialize AsciiMath OCR models
        self.tex2asciimath = Tex2ASCIIMath(log=False, inplace=True)
        logging.info("AsciiMath OCR Models Initialized!!!")

        # Downloaded image path and image properties
        self.downloaded_file_path = os.path.join(DOWNLOADED_IMAGE_PATH)
        self.image_width = None
        self.image_height = None

        # Image Source & Language
        self.image_url: Optional[str] = ""
        self.language: str = ""

        # Advanced Text Extraction
        self.advanced_text_extraction = False

        # Language Comparison Dictionary
        self.language_dictionary = {
            "CHINESE_SIM": self.latex_model_chinese_sim,
            "CHINESE_TRA": self.latex_model_chinese_tra,
            "KOREAN": self.latex_model_korean,
            "JAPANESE": self.latex_model_japanese,
            "ENGLISH": self.latex_model_english
        }

        # Formats and data options initialization
        self.formats: List[str] = []
        self.data_options = {}
        self.include_svg: bool = False
        self.include_table_html: bool = False
        self.include_latex: bool = False
        self.include_tsv: bool = False
        self.include_asciimath: bool = False
        self.include_mathml: bool = False
        self.include_text: bool = False

        # Format and Text Options initialization
        self.format_options = {}
        self.text_format_options: dict = {}
        self.text_math_delims: List[str] = []
        self.text_displaymath_delims: List[str] = []
        self.text_transforms: dict = {}

        # Text Transforms initialization
        self.text_rm_spaces: bool = False
        self.text_rm_newlines: bool = False
        self.text_rm_fonts: bool = False
        self.text_rm_style_syms: bool = False
        self.text_rm_text: bool = False
        self.text_long_frac: bool = False

        # Data Format and Transforms initialization
        self.data_format_options: dict = {}
        self.data_math_delims: List[str] = []
        self.data_displaymath_delims: List[str] = []
        self.data_transforms: dict = {}

        # Data Transforms initialization
        self.data_rm_spaces: bool = False
        self.data_rm_newlines: bool = False
        self.data_rm_fonts: bool = False
        self.data_rm_style_syms: bool = False
        self.data_rm_text: bool = False
        self.data_long_frac: bool = False

    @staticmethod
    def _initialize_latex_model(language_code: str) -> Pix2Text:
        """Helper function to initialize Pix2Text model based on language code."""
        config = {
            'text_formula': {'languages': ('en', language_code)},
        }
        return Pix2Text.from_config(total_configs=config, device="cuda")



# Create an instance of your Flask app
app = MyFlaskApp(__name__)


@app.route('/convert_text', methods=['POST'])
def convert_text():
    try:
        request_id = generate_request_id()

        # Parse incoming request data
        request_data = parse_request_data(request)
        assign_values_from_request(request_data, app=app)

        # Download image
        downloaded_file_path = check_url_and_download_image(image_url=app.image_url, request_id=request_id, app=app)
        if isinstance(downloaded_file_path, dict):
            return downloaded_file_path

        app.image_width, app.image_height = extract_image_size(downloaded_file_path)

        # Extract data from image
        (latex_styled_result, latex_confidence, is_handwritten,
         is_diagram_available, confidence_per_line) = extract_data_from_image(downloaded_file_path, app, request_id)

        # Convert to ASCII
        data_ascii_result, text_result = convert_to_ascii(latex_styled_result, app, request_id)

        # Advanced text extraction
        advanced_text_result = advanced_text_extraction(app, downloaded_file_path, request_id)

        # If text result is empty, use ASCII result
        if not text_result.strip():
            text_result = "".join([item["value"] for item in data_ascii_result if item["type"] == "asciimath"])

        # Clean latex styled result
        latex_styled_result = re.sub(r'\\{2,}', r'\\', latex_styled_result)

        # Prepare the final data result
        final_data_result = []
        if app.include_text:
            final_data_result.append({"type": TEXT, "value": text_result})
        if app.include_asciimath:
            final_data_result += data_ascii_result
        if app.include_latex:
            final_data_result.append({"type": LATEX, "value": latex_styled_result})

        # Construct and return the response
        return construct_response(
            app, request_id, text_result, advanced_text_result, latex_styled_result, final_data_result,
            is_handwritten, is_diagram_available, latex_confidence, confidence_per_line
        )

    except Exception as e:
        # Error handling
        error = str(e)
        logging.error(f"E_OCR_006 -> Request id : {request_id} -> Error: {error}")
        response_dict = {
            "request_id": request_id,
            "version": app.api_version,
            "image_width": app.image_width,
            "image_height": app.image_height,
            "error": error,
            "url": app.image_url
        }
        return jsonify(response_dict)

@app.route('/convert_text_multipart', methods=['POST'])
def convert_text_multipart():
    try:
        request_id = generate_request_id()

        # Validate the file in the request
        valid, error = validate_file(request, request_id)
        if not valid:
            return jsonify({
                "request_id": request_id,
                "version": app.api_version,
                "error": error
            })

        file = request.files['file']
        file_path = save_file(file, request_id, app)

        # Extract image size
        app.image_width, app.image_height = extract_image_size(file_path)

        # Parse form data
        request_data = parse_form_data(request)
        assign_values_from_request(request_data, app=app)

        # Process the image
        (latex_styled_result, latex_confidence, is_handwritten,
         is_diagram_available, confidence_per_line) = extract_data_from_image(file_path, app, request_id)

        # Convert to ASCII
        data_ascii_result, text_result = convert_to_ascii(latex_styled_result, app, request_id)

        # Advanced text extraction if enabled
        advanced_extracted_text = advanced_text_extraction(app, file_path, request_id)

        # If no text result, use the ASCII result
        if not text_result.strip():
            text_result = "".join([item["value"] for item in data_ascii_result if item["type"] == "asciimath"])

        latex_styled_result = re.sub(r'\\{2,}', r'\\', latex_styled_result)

        # Prepare final data result
        final_data_result = []
        if app.include_text:
            final_data_result.append({"type": TEXT, "value": text_result})
        if app.include_asciimath:
            final_data_result += data_ascii_result
        if app.include_latex:
            final_data_result.append({"type": LATEX, "value": latex_styled_result})

        # Construct and return the response
        return construct_response(
            app, request_id, text_result, advanced_extracted_text, latex_styled_result, final_data_result,
            is_handwritten, is_diagram_available, latex_confidence, confidence_per_line
        )

    except Exception as e:
        # Error handling
        error = str(e)
        logging.error(f"E_OCR_009 -> Request id : {request_id} -> Error: {error}")
        return jsonify({
            "request_id": request_id,
            "version": app.api_version,
            "image_width": app.image_width,
            "image_height": app.image_height,
            "error": error
        })


if __name__ == '__main__':
    app.run(debug=True)

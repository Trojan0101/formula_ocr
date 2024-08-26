"""
Title: API Entry Point
Author: Trojan
Date: 25-06-2024
"""
import json
import logging
import os
from typing import List, Optional
from urllib.parse import urlparse

import requests
from flask import Flask, request, jsonify
from pix2text import Pix2Text
from PIL import Image
from py_asciimath.translator.translator import Tex2ASCIIMath

from data_extractors.asciimath_converter import AsciimathConverter
from data_extractors.latex_extractor import LatexExtractor
from data_extractors.text_extractor import TextExtractor

import uuid

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')


class MyFlaskApp(Flask):
    def __init__(self, import_name):
        super().__init__(import_name)
        self.api_version = "1.0"
        self.latex_model_english = Pix2Text()
        pix_text_config_korean = {
            'text_formula': {'languages': ('en', 'ko')},
        }
        self.latex_model_korean = Pix2Text.from_config(total_configs=pix_text_config_korean)
        pix_text_config_japanese = {
            'text_formula': {'languages': ('en', 'ja')},
        }
        self.latex_model_japanese = Pix2Text.from_config(total_configs=pix_text_config_japanese)
        pix_text_config_chinese_sim = {
            'text_formula': {'languages': ('en', 'ch_sim')},
        }
        self.latex_model_chinese_sim = Pix2Text.from_config(total_configs=pix_text_config_chinese_sim)
        pix_text_config_chinese_tra = {
            'text_formula': {'languages': ('en', 'ch_tra')},
        }
        self.latex_model_chinese_tra = Pix2Text.from_config(total_configs=pix_text_config_chinese_tra)
        logging.info("Math OCR Models Initialized!!!")
        self.tex2asciimath = Tex2ASCIIMath(log=False, inplace=True)
        logging.info("AsciiMath OCR Models Initialized!!!")

        # Downloaded image path
        self.downloaded_file_path = os.path.join("downloaded_images", "verification_image.png")
        self.image_width = None
        self.image_height = None

        # Image Source
        self.image_url: Optional[str] = ""

        # Langugae
        self.language: str = ""

        # Language comparison
        self.language_dictionary = {
            # Keyword: [[tesseract_language], [pix2text language]]
            "CHINESE_SIM": [["eng", "chi_sim"], self.latex_model_chinese_sim],
            "CHINESE_TRA": [["eng", "chi_tra"], self.latex_model_chinese_tra],
            "KOREAN": [["eng", "kor"], self.latex_model_korean],
            "JAPANESE": [["eng", "jpn"], self.latex_model_japanese],
            "ENGLISH": [["eng"], self.latex_model_english]
        }

        # Formats (text and data)
        self.formats: List[str] = []

        # Data Options
        self.data_options = {}
        self.include_svg: bool = False
        self.include_table_html: bool = False
        self.include_latex: bool = False
        self.include_tsv: bool = False
        self.include_asciimath: bool = False
        self.include_mathml: bool = False
        self.include_text: bool = False

        # Format Options
        self.format_options = {}

        # Text Format Options (Latex styled)
        self.text_format_options: dict = {}
        self.text_math_delims: List[str] = []
        self.text_displaymath_delims: List[str] = []
        self.text_transforms: dict = {}

        # Text Transforms
        self.text_rm_spaces: bool = False
        self.text_rm_newlines: bool = False
        self.text_rm_fonts: bool = False
        self.text_rm_style_syms: bool = False
        self.text_rm_text: bool = False
        self.text_long_frac: bool = False

        # Data Format Options (Asciimath)
        self.data_format_options: dict = {}
        self.data_math_delims: List[str] = []
        self.data_displaymath_delims: List[str] = []
        self.data_transforms: dict = {}

        # Data Transforms
        self.data_rm_spaces: bool = False
        self.data_rm_newlines: bool = False
        self.data_rm_fonts: bool = False
        self.data_rm_style_syms: bool = False
        self.data_rm_text: bool = False
        self.data_long_frac: bool = False

        # Logging
        logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')


# Create an instance of your Flask app
app = MyFlaskApp(__name__)


@app.route('/convert_text', methods=['POST'])
def convert_text():
    request_id = str(uuid.uuid4())

    # Request data
    json_string = request.data.decode('utf-8')
    request_data = json.loads(json_string, strict=False)

    # Assign values from request
    assign_values_from_request(request_data)

    # Check URL and download image
    url_check = check_url_and_download_image(image_url=app.image_url, request_id=request_id)

    if url_check is not None:
        return url_check

    # Start data extraction
    try:
        # Initialize variables for results
        text_result = ""
        latex_styled_result = ""
        ascii_result = ""

        if app.language is not None:
            latex_extractor = LatexExtractor()
            latex_styled_result, latex_confidence = latex_extractor.recognize_image_single_language(
                model=app.language_dictionary[app.language][1], request_id=request_id, language=app.language)

            # text_extractor = TextExtractor(language=app.language_dictionary[app.language][0])
            # text_result, is_handwritten = text_extractor.convert_image_to_text(request_id=request_id)
        else:
            latex_extractor = LatexExtractor(
                latex_model_english=app.latex_model_english,
                latex_model_korean=app.latex_model_korean,
                latex_model_japanese=app.latex_model_japanese,
                latex_model_chinese_sim=app.latex_model_chinese_sim,
                latex_model_chinese_tra=app.latex_model_chinese_tra
            )
            latex_styled_result, latex_confidence, tesseract_language = latex_extractor.recognize_image(request_id=request_id)

            # text_extractor = TextExtractor(language=tesseract_language)
            # text_result, is_handwritten = text_extractor.convert_image_to_text(request_id=request_id)

        is_handwritten = False
        ascii_converter = AsciimathConverter(converter_model=app.tex2asciimath)
        data_ascii_result, text_result = ascii_converter.convert_to_ascii(request_id=request_id, latex_expression=latex_styled_result)

        if text_result.strip() == "":
            text_result = [[item["value"] for item in data_ascii_result if item["type"] == "asciimath"] if text_result.strip() == "" else text_result][0]
            text_result = "".join(text_result)

        data_latex_result = {
            "type": "latex",
            "value": latex_styled_result
        }

        data_text_result = {
            "type": "text",
            "value": text_result
        }

        final_data_result = []

        if app.include_text:
            final_data_result.append(data_text_result)
        if app.include_asciimath:
            # data_ascii_result is already a list
            final_data_result += data_ascii_result
        if app.include_latex:
            final_data_result.append(data_latex_result)

        if "text" in app.formats and "data" in app.formats:
            response_dict = {
                "request_id": request_id,
                "version": app.api_version,
                "image_width": app.image_width,
                "image_height": app.image_height,
                "is_printed": not is_handwritten,
                "is_handwritten": is_handwritten,
                "text": text_result,
                "latex_styled": latex_styled_result,
                "confidence": latex_confidence,
                "data": final_data_result,
                "url": app.image_url
            }
            return jsonify(response_dict)
        elif "text" in app.formats and "data" not in app.formats:
            response_dict = {
                "request_id": request_id,
                "version": app.api_version,
                "image_width": app.image_width,
                "image_height": app.image_height,
                "is_printed": not is_handwritten,
                "is_handwritten": is_handwritten,
                "text": text_result,
                "latex_styled": latex_styled_result,
                "confidence": latex_confidence,
                "url": app.image_url
            }
            return jsonify(response_dict)
        elif "data" in app.formats and "text" not in app.formats:
            response_dict = {
                "request_id": request_id,
                "version": app.api_version,
                "image_width": app.image_width,
                "image_height": app.image_height,
                "is_printed": not is_handwritten,
                "is_handwritten": is_handwritten,
                "data": final_data_result,
                "confidence": latex_confidence,
                "url": app.image_url
            }
            return jsonify(response_dict)
    except Exception as e:
        error = str(e)
        logging.error(f"Request id : {request_id} -> Error: {error}")
        response_dict = {
            "request_id": request_id,
            "version": app.api_version,
            "image_width": app.image_width,
            "image_height": app.image_height,
            "error": error,
            "url": app.image_url
        }

        return jsonify(response_dict)


def assign_values_from_request(request_data: dict):
    # Image Source
    app.image_url = request_data.get("src", None)

    # Language
    app.language = request_data.get("language", None)

    # Formats (text and data)
    app.formats = request_data.get("formats", [])

    # Data Options
    app.data_options = request_data.get("data_options", {})
    app.include_svg = app.data_options.get("include_svg", False)
    app.include_table_html = app.data_options.get("include_table_html", False)
    app.include_latex = app.data_options.get("include_latex", False)
    app.include_tsv = app.data_options.get("include_tsv", False)
    app.include_asciimath = app.data_options.get("include_asciimath", False)
    app.include_mathml = app.data_options.get("include_mathml", False)
    app.include_text = app.data_options.get("include_text", False)

    # Format Options
    app.format_options = request_data.get("format_options", {})

    # Text Format Options (Latex styled)
    app.text_format_options = app.format_options.get("text", {})
    app.text_math_delims = app.text_format_options.get("math_delims", [])
    app.text_displaymath_delims = app.text_format_options.get("displaymath_delims", [])
    app.text_transforms = app.text_format_options.get("transforms", {})

    # Text Transforms
    app.text_rm_spaces = app.text_transforms.get("rm_spaces", False)
    app.text_rm_newlines = app.text_transforms.get("rm_newlines", False)
    app.text_rm_fonts = app.text_transforms.get("rm_fonts", False)
    app.text_rm_style_syms = app.text_transforms.get("rm_style_syms", False)
    app.text_rm_text = app.text_transforms.get("rm_text", False)
    app.text_long_frac = app.text_transforms.get("long_frac", False)

    # Data Format Options (Asciimath)
    app.data_format_options = app.format_options.get("data", {})
    app.data_math_delims = app.data_format_options.get("math_delims", [])
    app.data_displaymath_delims = app.data_format_options.get("displaymath_delims", [])
    app.data_transforms = app.data_format_options.get("transforms", {})

    # Data Transforms
    app.data_rm_spaces = app.data_transforms.get("rm_spaces", False)
    app.data_rm_newlines = app.data_transforms.get("rm_newlines", False)
    app.data_rm_fonts = app.data_transforms.get("rm_fonts", False)
    app.data_rm_style_syms = app.data_transforms.get("rm_style_syms", False)
    app.data_rm_text = app.data_transforms.get("rm_text", False)
    app.data_long_frac = app.data_transforms.get("long_frac", False)


def check_url_and_download_image(image_url: str, request_id: str):
    parsed_url = urlparse(image_url)
    if parsed_url.scheme and parsed_url.netloc:
        try:
            response = requests.get(image_url)
            response.raise_for_status()
            with open(app.downloaded_file_path, 'wb') as f:
                f.write(response.content)
            with Image.open(app.downloaded_file_path) as img:
                app.image_width, app.image_height = img.size
            return None
        except Exception as e:
            error = str(e)
            logging.error(f"Request id : {request_id} -> Error with exception: {error}")
            response_dict = {
                "request_id": request_id,
                "version": app.api_version,
                "image_width": app.image_width,
                "image_height": app.image_height,
                "error": error
            }
            return jsonify(response_dict)
    else:
        error = str({"error": "Invalid URL format"})
        logging.error(f"Request id : {request_id} -> Error: {error}")
        response_dict = {
            "request_id": request_id,
            "version": app.api_version,
            "error": error
        }
        return jsonify(response_dict)


if __name__ == '__main__':
    app.run(debug=True)

"""
Title: API Entry Point
Author: Trojan
Date: 25-06-2024
"""
import json
import logging
import os
import re
from typing import List, Optional, Union
from urllib.parse import urlparse

import requests
from flask import Flask, request, jsonify, Response
from pix2text import Pix2Text
from PIL import Image
from py_asciimath.translator.translator import Tex2ASCIIMath

from data_extractors.advanced_text_extractor import AdvancedTextExtractor
from data_extractors.asciimath_converter import AsciimathConverter
from data_extractors.latex_extractor import LatexExtractor

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
        self.downloaded_file_path = os.path.join("downloaded_images")
        self.image_width = None
        self.image_height = None

        # Image Source
        self.image_url: Optional[str] = ""

        # Langugae
        self.language: str = ""

        # Advanced Text Extraction
        self.advanced_text_extraction = False

        # Language comparison
        self.language_dictionary = {
            # Keyword: pix2text language
            "CHINESE_SIM": self.latex_model_chinese_sim,
            "CHINESE_TRA": self.latex_model_chinese_tra,
            "KOREAN": self.latex_model_korean,
            "JAPANESE": self.latex_model_japanese,
            "ENGLISH": self.latex_model_english
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
    downloaded_file_path = check_url_and_download_image(image_url=app.image_url, request_id=request_id)

    if isinstance(downloaded_file_path, dict):
        return downloaded_file_path
    else:
        pass

    # Start data extraction
    try:
        # Initialize variables for results
        text_result = ""
        latex_styled_result = ""
        ascii_result = ""

        if app.language is not None:
            latex_extractor = LatexExtractor(downloaded_file_path)
            latex_styled_result, latex_confidence, is_handwritten, is_diagram_available, confidence_per_line = latex_extractor.recognize_image_single_language(
                model=app.language_dictionary[app.language], request_id=request_id, language=app.language)
        else:
            latex_extractor = LatexExtractor(
                downloaded_file_path=downloaded_file_path,
                latex_model_english=app.latex_model_english,
                latex_model_korean=app.latex_model_korean,
                latex_model_japanese=app.latex_model_japanese,
                latex_model_chinese_sim=app.latex_model_chinese_sim,
                latex_model_chinese_tra=app.latex_model_chinese_tra
            )
            latex_styled_result, latex_confidence, is_handwritten, is_diagram_available, confidence_per_line = latex_extractor.recognize_image(request_id=request_id)

        ascii_converter = AsciimathConverter(converter_model=app.tex2asciimath)
        data_ascii_result, text_result = ascii_converter.convert_to_ascii(request_id=request_id, latex_expression=latex_styled_result)

        advanced_extracted_text = "Provide 'advanced_text_extraction' as True is the request!!!"
        if app.advanced_text_extraction and app.language is not None:
            advanced_extracted_text = AdvancedTextExtractor(downloaded_file_path, language=app.language)

        if text_result.strip() == "":
            text_result = [[item["value"] for item in data_ascii_result if item["type"] == "asciimath"] if text_result.strip() == "" else text_result][0]
            text_result = "".join(text_result)

        latex_styled_result = re.sub(r'\\{2,}', r'\\', latex_styled_result)
        data_latex_result = {
            "type": "latex",
            "value": latex_styled_result
        }

        data_text_result = {
            "type": "text",
            "value": text_result
        }

        advanced_text_result = {
            "type": "text",
            "value": advanced_extracted_text
        }

        final_data_result = []

        if app.include_text:
            final_data_result.append(data_text_result)
        if app.include_asciimath:
            # data_ascii_result is already a list
            final_data_result += data_ascii_result
        if app.include_latex:
            final_data_result.append(data_latex_result)
        
        if app.advanced_text_extraction:
            final_data_result.append(advanced_text_result)

        if "text" in app.formats and "data" in app.formats:
            response_dict = {
                "request_id": request_id,
                "version": app.api_version,
                "image_width": app.image_width,
                "image_height": app.image_height,
                "is_printed": not is_handwritten,
                "is_handwritten": is_handwritten,
                "is_diagram_available": is_diagram_available,
                "text": text_result,
                "advanced_text": advanced_text_result,
                "latex_styled": latex_styled_result,
                "confidence": latex_confidence,
                "confidence_per_line": confidence_per_line,
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
                "is_diagram_available": is_diagram_available,
                "text": text_result,
                "advanced_text": advanced_text_result,
                "latex_styled": latex_styled_result,
                "confidence": latex_confidence,
                "confidence_per_line": confidence_per_line,
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
                "is_diagram_available": is_diagram_available,
                "data": final_data_result,
                "confidence": latex_confidence,
                "confidence_per_line": confidence_per_line,
                "url": app.image_url
            }
            return jsonify(response_dict)
    except Exception as e:
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
    request_id = str(uuid.uuid4())

    if 'file' not in request.files:
        error = "No file part"
        logging.error(f"E_OCR_007 -> Request id : {request_id} -> Error: {error}")
        response_dict = {
            "request_id": request_id,
            "version": app.api_version,
            "error": error
        }
        return jsonify(response_dict)

    file = request.files['file']
    if file.filename == '':
        error = "No selected file"
        logging.error(f"E_OCR_008 -> Request id : {request_id} -> Error: {error}")
        response_dict = {
            "request_id": request_id,
            "version": app.api_version,
            "error": error
        }
        return jsonify(response_dict)

    # Save the file
    file_path = os.path.join(app.downloaded_file_path, f"{request_id}.png")
    file.save(file_path)

    # Extract image size
    with Image.open(file_path) as img:
        app.image_width, app.image_height = img.size

    # Extract parameters from form-data
    request_data = {
        "language": request.form.get("language"),
        "formats": request.form.getlist("formats"),
        "data_options": json.loads(request.form.get("data_options", '{}')),
        "format_options": json.loads(request.form.get("format_options", '{}'))
    }

    # Assign values from the processed request_data
    assign_values_from_request(request_data)

    # Process image
    try:
        text_result = ""
        latex_styled_result = ""
        ascii_result = ""
        if app.language is not None:
            latex_extractor = LatexExtractor(file_path)
            latex_styled_result, latex_confidence, is_handwritten, is_diagram_available, confidence_per_line = latex_extractor.recognize_image_single_language(
                model=app.language_dictionary[app.language], request_id=request_id, language=app.language)
        else:
            latex_extractor = LatexExtractor(
                downloaded_file_path=file_path,
                latex_model_english=app.latex_model_english,
                latex_model_korean=app.latex_model_korean,
                latex_model_japanese=app.latex_model_japanese,
                latex_model_chinese_sim=app.latex_model_chinese_sim,
                latex_model_chinese_tra=app.latex_model_chinese_tra
            )
            latex_styled_result, latex_confidence, is_handwritten, is_diagram_available, confidence_per_line = latex_extractor.recognize_image(request_id=request_id)

        ascii_converter = AsciimathConverter(converter_model=app.tex2asciimath)
        data_ascii_result, text_result = ascii_converter.convert_to_ascii(request_id=request_id, latex_expression=latex_styled_result)

        advanced_extracted_text = "Provide 'advanced_text_extraction' as True is the request!!!"
        if app.advanced_text_extraction and app.language is not None:
            advanced_extracted_text = AdvancedTextExtractor(file_path, language=app.language)
        
        if text_result.strip() == "":
            text_result = [[item["value"] for item in data_ascii_result if item["type"] == "asciimath"] if text_result.strip() == "" else text_result][0]
            text_result = "".join(text_result)

        latex_styled_result = re.sub(r'\\{2,}', r'\\', latex_styled_result)
        data_latex_result = {
            "type": "latex",
            "value": latex_styled_result
        }

        data_text_result = {
            "type": "text",
            "value": text_result
        }

        advanced_text_result = {
            "type": "text",
            "value": advanced_extracted_text
        }

        final_data_result = []

        if app.include_text:
            final_data_result.append(data_text_result)
        if app.include_asciimath:
            final_data_result += data_ascii_result
        if app.include_latex:
            final_data_result.append(data_latex_result)
        
        if app.advanced_text_extraction:
            final_data_result.append(advanced_text_result)

        if "text" in app.formats and "data" in app.formats:
            response_dict = {
                "request_id": request_id,
                "version": app.api_version,
                "image_width": app.image_width,
                "image_height": app.image_height,
                "is_printed": not is_handwritten,
                "is_handwritten": is_handwritten,
                "is_diagram_available": is_diagram_available,
                "text": text_result,
                "advanced_text": advanced_text_result,
                "latex_styled": latex_styled_result,
                "confidence": latex_confidence,
                "confidence_per_line": confidence_per_line,
                "data": final_data_result
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
                "is_diagram_available": is_diagram_available,
                "text": text_result,
                "advanced_text": advanced_text_result,
                "latex_styled": latex_styled_result,
                "confidence": latex_confidence,
                "confidence_per_line": confidence_per_line,
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
                "is_diagram_available": is_diagram_available,
                "data": final_data_result,
                "confidence": latex_confidence,
                "confidence_per_line": confidence_per_line,
            }
            return jsonify(response_dict)
    except Exception as e:
        error = str(e)
        logging.error(f"E_OCR_009 -> Request id : {request_id} -> Error: {error}")
        response_dict = {
            "request_id": request_id,
            "version": app.api_version,
            "image_width": app.image_width,
            "image_height": app.image_height,
            "error": error
        }
        return jsonify(response_dict)


def assign_values_from_request(request_data: dict):
    # Image Source
    app.image_url = request_data.get("src", None)

    # Language
    app.language = request_data.get("language", None)

    # Advanced Text Extraction
    app.advanced_text_extraction = request_data.get("advanced_text_extraction", False)

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


def check_url_and_download_image(image_url: str, request_id: str) -> Union[Response, str]:
    parsed_url = urlparse(image_url)
    new_downloaded_file_path = app.downloaded_file_path + f"/{request_id}.png"
    if parsed_url.scheme and parsed_url.netloc:
        try:
            response = requests.get(image_url)
            response.raise_for_status()
            with open(new_downloaded_file_path, 'wb') as f:
                f.write(response.content)
            with Image.open(new_downloaded_file_path) as img:
                app.image_width, app.image_height = img.size
            return new_downloaded_file_path
        except Exception as e:
            error = str(e)
            logging.error(f"E_OCR_010 -> Request id : {request_id} -> Error with exception: {error}")
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
        logging.error(f"E_OCR_011 -> Request id : {request_id} -> Error: {error}")
        response_dict = {
            "request_id": request_id,
            "version": app.api_version,
            "error": error
        }
        return jsonify(response_dict)


if __name__ == '__main__':
    app.run(debug=True)

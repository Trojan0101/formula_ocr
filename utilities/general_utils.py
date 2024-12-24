"""
Title: General utils
Author: Trojan
Date: 25-06-2024
"""
from typing import Union
from urllib.parse import urlparse
import requests
from flask import jsonify, Response
from PIL import Image


def assign_values_from_request(request_data: dict, app):
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


def check_url_and_download_image(image_url: str, request_id: str, app) -> Union[Response, str]:
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
            error_dict = {"code": "E_OCR_010", "message": f"Error with exception: {str(e)}"}
            logging.error(error_dict)
            response_dict = {
                "status": 1,
                "request_id": request_id,
                "version": app.api_version,
                "image_width": app.image_width,
                "image_height": app.image_height,
                "error": error_dict
            }
            return jsonify(response_dict)
    else:
        error_dict = {"code": "E_OCR_011", "message": f"Invalid URL format"}
        logging.error(error_dict)
        response_dict = {
            "status": 1,
            "request_id": request_id,
            "version": app.api_version,
            "error": error_dict
        }
        return jsonify(response_dict)

import logging

def setup_logging(level=logging.DEBUG):
    """
    Set up logging configuration that can be reused across the application.

    :param level: Logging level to be set (default is DEBUG)
    """
    logging.basicConfig(level=level, format='%(asctime)s - %(levelname)s - %(message)s')

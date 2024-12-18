"""
Title: Core utils
Author: Trojan
Date: 25-06-2024
"""
import os
import uuid
import json
import logging
from flask import jsonify
from super_image import EdsrModel
from PIL import Image
from data_extractors.advanced_text_extractor import AdvancedTextExtractor
from data_extractors.asciimath_converter import AsciimathConverter
from data_extractors.latex_extractor import LatexExtractor

# Constants for repeated keys
LATEX = "latex"
TEXT = "text"
DATA = "data"
ADVANCED_TEXT = "advanced_text"


def generate_request_id():
    """Generate a unique request ID."""
    return str(uuid.uuid4())


def parse_request_data(request):
    """Parse incoming JSON request data."""
    json_string = request.data.decode('utf-8')
    return json.loads(json_string, strict=False)


def extract_data_from_image(downloaded_file_path, app, request_id):
    """Extract data from the downloaded image based on the language."""
    if app.language:
        latex_extractor = LatexExtractor(downloaded_file_path)
        return latex_extractor.recognize_image_single_language(
            model=app.language_dictionary[app.language], request_id=request_id
        )
    else:
        latex_extractor = LatexExtractor(
            downloaded_file_path=downloaded_file_path,
            latex_model_english=app.latex_model_english,
            latex_model_korean=app.latex_model_korean,
            latex_model_japanese=app.latex_model_japanese,
            latex_model_chinese_sim=app.latex_model_chinese_sim,
            latex_model_chinese_tra=app.latex_model_chinese_tra
        )
        return latex_extractor.recognize_image(request_id=request_id)


def convert_to_ascii(latex_styled_result, app, request_id):
    """Convert latex to ASCII format."""
    ascii_converter = AsciimathConverter(converter_model=app.tex2asciimath)
    return ascii_converter.convert_to_ascii(request_id=request_id, latex_expression=latex_styled_result)


def advanced_text_extraction(app, downloaded_file_path, request_id):
    """Perform advanced text extraction if enabled."""
    if app.advanced_text_extraction and app.language:
        model = EdsrModel.from_pretrained('eugenesiow/edsr-base', scale=4)
        advanced_text_extractor = AdvancedTextExtractor(downloaded_file_path, language=app.language)
        return advanced_text_extractor.extract_text(model, request_id)
    return None


def construct_response(app, request_id, text_result, advanced_text_result, latex_styled_result, final_data_result,
                       is_handwritten, is_diagram_available, latex_confidence, confidence_per_line):
    """Construct the appropriate response based on the requested formats."""
    response_dict = {
        "request_id": request_id,
        "version": app.api_version,
        "image_width": app.image_width,
        "image_height": app.image_height,
        "is_printed": not is_handwritten,
        "is_handwritten": is_handwritten,
        "is_diagram_available": is_diagram_available,
        "text": text_result,
        "latex_styled": latex_styled_result,
        "confidence": latex_confidence,
        "confidence_per_line": confidence_per_line,
        "url": app.image_url
    }

    if app.advanced_text_extraction:
        response_dict["advanced_text"] = {"type": "text", "value": advanced_text_result}

    if "text" in app.formats and "data" in app.formats:
        response_dict["data"] = final_data_result
    elif "data" in app.formats and "text" not in app.formats:
        response_dict = {key: response_dict[key] for key in response_dict if
                         key not in ["text", "advanced_text", "latex_styled"]}
        response_dict["data"] = final_data_result
    elif "text" in app.formats and "data" not in app.formats:
        response_dict = {key: response_dict[key] for key in response_dict if key not in ["data"]}

    return jsonify(response_dict)


def validate_file(request, request_id):
    """Validate if a file is included in the request and is not empty."""
    if 'file' not in request.files:
        error = "No file part"
        logging.error(f"E_OCR_007 -> Request id : {request_id} -> Error: {error}")
        return False, error

    file = request.files['file']
    if file.filename == '':
        error = "No selected file"
        logging.error(f"E_OCR_008 -> Request id : {request_id} -> Error: {error}")
        return False, error

    return True, file


def save_file(file, request_id, app):
    """Save the uploaded file and return the file path."""
    file_path = os.path.join(app.downloaded_file_path, f"{request_id}.png")
    file.save(file_path)
    return file_path


def extract_image_size(file_path):
    """Extract image dimensions."""
    with Image.open(file_path) as img:
        return img.size


def parse_form_data(request):
    """Parse form data including language, formats, and other options."""
    return {
        "language": request.form.get("language"),
        "formats": request.form.getlist("formats"),
        "data_options": json.loads(request.form.get("data_options", '{}')),
        "format_options": json.loads(request.form.get("format_options", '{}')),
        "advanced_text_extraction": json.loads(request.form.get("advanced_text_extraction", False))
    }
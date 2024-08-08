"""
Title: API Entry Point
Author: Trojan
Date: 25-06-2024
"""
import logging
import os
from urllib.parse import urlparse

import requests
from flask import Flask, request, jsonify
from pix2text import Pix2Text
from rapid_latex_ocr import LatexOCR
from PIL import Image

from data_extractors.latex_extractor import LatexExtractor
from data_extractors.latex_extractor_mixed import LatexExtractorMixed
from data_extractors.text_extractor import TextExtractor

import uuid

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')


class MyFlaskApp(Flask):
    def __init__(self, import_name):
        super().__init__(import_name)
        self.latex_model_mixed = None
        self.latex_model = None
        self.setup_latex_model()

    def setup_latex_model(self):
        # Initialize LatexOCR here
        self.latex_model = LatexOCR()
        self.latex_model_mixed = Pix2Text(languages=('en', 'ko', 'ch_sim', 'ch_tra', 'ja'))
        logging.info("Math OCR Models Initialized!!!")


# Create an instance of your Flask app
app = MyFlaskApp(__name__)


@app.route('/convert_text', methods=['POST'])
def convert_text():
    api_version = "1.0"
    request_id = str(uuid.uuid4())
    downloaded_file_path = os.path.join("downloaded_images", "verification_image.png")
    image_width = 0
    image_height = 0
    logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

    request_data = request.get_json()
    image_url = request_data.get("src")

    # Check URL and download image
    parsed_url = urlparse(image_url)
    if parsed_url.scheme and parsed_url.netloc:
        try:
            response = requests.get(image_url)
            response.raise_for_status()
            with open(downloaded_file_path, 'wb') as f:
                f.write(response.content)
            with Image.open(downloaded_file_path) as img:
                image_width, image_height = img.size
        except Exception as e:
            logging.error(f"Request id : {request_id} -> Error with exception: {e}")
            final_response = {
                "request_id": request_id,
                "version": api_version,
                "image_width": image_width,
                "image_height": image_height,
                "error": str(e)
            }
            return jsonify(final_response)
    else:
        logging.error(f"Request id : {request_id} -> Error: Invalid URL format")
        final_response = {
            "request_id": request_id,
            "version": api_version,
            "error": str({"error": "Invalid URL format"})
        }
        return jsonify(final_response)

    # Start data extraction
    try:
        text_extractor = TextExtractor()
        response_data_text = text_extractor.convert_image_to_text(request_id=request_id)

        latex_extractor = LatexExtractor(app.latex_model)
        response_data_latex = latex_extractor.convert_image_to_latex(request_id=request_id)

        latex_extractor_mixed = LatexExtractorMixed(app.latex_model_mixed)
        response_data_latex_mixed = latex_extractor_mixed.recognize_image(request_id=request_id)

        final_response = {
            "request_id": request_id,
            "version": api_version,
            "image_width": image_width,
            "image_height": image_height,
            "text": response_data_text["text"],
            "latex_styled_1": response_data_latex["latex_text"],
            "latex_styled_2": response_data_latex_mixed
        }
    except Exception as e:
        final_response = {
            "request_id": request_id,
            "version": api_version,
            "image_width": image_width,
            "image_height": image_height,
            "error": str(e)
        }

    return jsonify(final_response)


if __name__ == '__main__':
    app.run(debug=True)

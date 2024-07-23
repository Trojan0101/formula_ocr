"""
Title: API Entry Point
Author: Trojan
Date: 25-06-2024
"""

from flask import Flask, request, jsonify

from data_extractors.latex_extractor import LatexExtractor
from data_extractors.text_extractor import TextExtractor

app = Flask(__name__)


@app.route('/convert_latex', methods=['POST'])
def convert_latex():
    request_data = request.get_json()
    image_url = request_data.get("src")

    try:
        latex_extractor = LatexExtractor()
        response_data = latex_extractor.convert_image_to_latex(url=image_url)
    except Exception as e:
        response_data = {"error": str(e)}

    return jsonify(response_data)


@app.route('/convert_text', methods=['POST'])
def convert_text():
    request_data = request.get_json()
    image_url = request_data.get("src")
    image_language = [x.strip() for x in request_data.get("language").split(",")]

    try:
        text_extractor = TextExtractor(image_language)
        response_data = text_extractor.convert_image_to_text(url=image_url)
    except Exception as e:
        response_data = {"error": str(e)}

    return jsonify(response_data)


if __name__ == '__main__':
    app.run(debug=True)

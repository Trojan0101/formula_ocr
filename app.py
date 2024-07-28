"""
Title: API Entry Point
Author: Trojan
Date: 25-06-2024
"""

from flask import Flask, request, jsonify

from data_extractors.latex_extractor import LatexExtractor
from data_extractors.text_extractor import TextExtractor

app = Flask(__name__)


@app.route('/convert_text', methods=['POST'])
def convert_text():
    request_data = request.get_json()
    image_url = request_data.get("src")

    try:
        text_extractor = TextExtractor()
        response_data_text = text_extractor.convert_image_to_text(url=image_url)

        latex_extractor = LatexExtractor()
        response_data_latex = latex_extractor.convert_image_to_latex(url=image_url)
        final_response = {"text": response_data_text["text"], "latex": response_data_latex["latex_text"]}
    except Exception as e:
        final_response = {"error": str(e)}

    return jsonify(final_response)


if __name__ == '__main__':
    app.run(debug=True)

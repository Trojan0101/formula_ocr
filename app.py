"""
Title: API Entry Point
Author: Trojan
Date: 25-06-2024
"""

from flask import Flask, request, jsonify
from data_extractors.latex_extractor import LatexExtractor
from data_extractors.text_extractor import TextExtractor

import uuid

app = Flask(__name__)


@app.route('/convert_text', methods=['POST'])
def convert_text():
    api_version = "1.0"
    request_id = str(uuid.uuid4())
    
    request_data = request.get_json()
    image_url = request_data.get("src")

    try:
        text_extractor = TextExtractor()
        response_data_text = text_extractor.convert_image_to_text(url=image_url, request_id=request_id)

        latex_extractor = LatexExtractor()
        response_data_latex = latex_extractor.convert_image_to_latex(url=image_url, request_id=request_id)
        final_response = {
            "request_id": request_id,
            "version": api_version,
            "text": response_data_text["text"], 
            "latex_styled": response_data_latex["latex_text"]
            }
    except Exception as e:
        final_response = {
            "request_id": request_id,
            "version": api_version,
            "error": str(e)
            }

    return jsonify(final_response)


if __name__ == '__main__':
    app.run(debug=True)
    # serve(app, host='0.0.0.0', port=8080)

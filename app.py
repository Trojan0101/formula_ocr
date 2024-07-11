"""
Title: API Entry Point
Author: Trojan
Date: 25-06-2024
"""

from flask import Flask, request, jsonify

from data_extractors.latex_extractor import LatexExtractor

app = Flask(__name__)


@app.route('/convert_latex', methods=['POST'])
def convert_latex():
    request_data = request.get_json()
    image_url = request_data.get("src")
    image_language = request_data.get("language")

    try:
        latex_extractor = LatexExtractor()
        response_data = latex_extractor.convert_image_to_latex(url=image_url)
    except Exception as e:
        response_data = {"error": str(e)}

    return jsonify(response_data)


if __name__ == '__main__':
    app.run(debug=True)

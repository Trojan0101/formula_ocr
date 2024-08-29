"""
Title: LatexExtractorMixed
Author: Trojan
Date: 27-06-2024
"""
import logging
import os
from typing import Any, Optional
import cv2
import numpy as np

from PIL import Image

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')


class LatexExtractor:
    def __init__(self, latex_model_english: Optional[Any] = None, latex_model_korean: Optional[Any] = None,
                 latex_model_japanese: Optional[Any] = None, latex_model_chinese_sim: Optional[Any] = None,
                 latex_model_chinese_tra: Optional[Any] = None):
        self.latex_model_english = latex_model_english
        self.latex_model_korean = latex_model_korean
        self.latex_model_japanese = latex_model_japanese
        self.latex_model_chinese_sim = latex_model_chinese_sim
        self.latex_model_chinese_tra = latex_model_chinese_tra
        self.model_to_tesseract_code = {
            "self.latex_model_english": [["eng"], self.latex_model_english],
            "self.latex_model_korean": [['eng', 'kor'], self.latex_model_korean],
            "self.latex_model_japanese": [['eng', 'jpn'], self.latex_model_japanese],
            "self.latex_model_chinese_sim": [['eng', 'chi_sim'], self.latex_model_chinese_sim],
            "self.latex_model_chinese_tra": [['eng', 'chi_tra'], self.latex_model_chinese_tra],
        }
        self.downloaded_file_path = os.path.join("downloaded_images", "verification_image.png")

    def recognize_image(self, request_id: str):
        """Recognize text in the given image and optionally save the result."""
        try:
            image = Image.open(self.downloaded_file_path).convert('RGB')
            latex_results = {}
            count = 0
            for latex_model in self.model_to_tesseract_code:
                language = self.model_to_tesseract_code[latex_model][0]
                model = self.model_to_tesseract_code[latex_model][1]
                count += 1
                latex_data = model.recognize_text_formula(image, file_type='text_formula', return_text=False)
                latex_result = ""
                for data in latex_data:
                    latex_result += data.get("text", "")
                total_score = 0
                total_dicts = len(latex_data)
                for data in latex_data:
                    total_score += data["score"]
                final_confidence_score = total_score / total_dicts
                latex_results[f"model_{count}"] = {"text": latex_result, "confidence": final_confidence_score,
                                                   "language": language}

            highest_confidence_model = max(latex_results, key=lambda k: latex_results[k]['confidence'])
            highest_confidence = latex_results[highest_confidence_model]['confidence']
            highest_confidence_text = latex_results[highest_confidence_model]['text']
            highest_confidence_language = latex_results[highest_confidence_model]['language']

            logging.info(f"Request id : {request_id} -> Extracted Text LatexOCRMixed: {highest_confidence_text}")
        except Exception as e:
            logging.error(f"Request id : {request_id} -> Error with exception: {e}")
            return f"error: {str(e)}"
        return highest_confidence_text, highest_confidence, highest_confidence_language

    def recognize_image_single_language(self, model: Any, request_id: str, language: str):
        try:
            self.extract_and_remove_diagrams_from_image(request_id)
            image = Image.open(self.downloaded_file_path).convert('RGB')
            latex_results = {}
            latex_data = model.recognize_text_formula(image, file_type='text_formula', return_text=False)
            latex_result = ""
            for data in latex_data:
                latex_result += data.get("text", "")
            total_score = 0
            total_dicts = len(latex_data)
            for data in latex_data:
                total_score += data["score"]
            final_confidence_score = total_score / total_dicts
            latex_results[f"model_{language}"] = {"text": latex_result, "confidence": final_confidence_score,
                                                   "language": language}

            logging.info(f"Request id : {request_id} -> Extracted Text LatexOCRMixed: {latex_result}")

        except Exception as e:
            logging.error(f"Request id : {request_id} -> Error with exception: {e}")
            return f"error: {str(e)}"
        return latex_result, final_confidence_score

    def extract_and_remove_diagrams_from_image(self, request_id: str):
        # Load image
        image = cv2.imread(self.downloaded_file_path)

        try:
            original = image.copy()
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)[1]
            kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (20, 10))
            dilate = cv2.dilate(thresh, kernel, iterations=2)

            cnts, _ = cv2.findContours(dilate, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            for c in cnts:
                x, y, w, h = cv2.boundingRect(c)
                area = cv2.contourArea(c)
                if w / h > 2 and area > 10000:
                    cv2.drawContours(dilate, [c], -1, (0, 0, 0), -1)

            boxes = []
            cnts, _ = cv2.findContours(dilate, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            for c in cnts:
                x, y, w, h = cv2.boundingRect(c)
                boxes.append([x, y, x + w, y + h])

            if not boxes:
                logging.error(f"Request id : {request_id} -> No diagrams found in this image.")
                return

            for box in boxes:
                x, y, x2, y2 = box
                cv2.rectangle(image, (x, y), (x2, y2), (255, 255, 255), -1)

            cv2.imwrite(self.downloaded_file_path, image)
        except Exception as e:
            logging.error(f"Request id : {request_id} -> Not able to extract diagrams with error {e}.")
            pass

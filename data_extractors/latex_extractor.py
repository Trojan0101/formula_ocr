"""
Title: Latex extractor
Author: Trojan
Date: 25-06-2024
"""
from collections import Counter
import logging
import os
from typing import Any, Optional
from math import exp

import cv2
from PIL import Image

from ocrd_typegroups_classifier.typegroups_classifier import TypegroupsClassifier
from utilities.config import LOGGING_LEVEL
from utilities.custom_exception import CustomExceptionAndLog
from utilities.general_utils import setup_logging

# Logging Configuration
setup_logging(LOGGING_LEVEL)


class LatexExtractor:
    def __init__(self, downloaded_file_path: str, latex_model_english: Optional[Any] = None,
                 latex_model_korean: Optional[Any] = None, latex_model_japanese: Optional[Any] = None,
                 latex_model_chinese_sim: Optional[Any] = None, latex_model_chinese_tra: Optional[Any] = None):
        """
        Initialize the LatexExtractor class with models and file path.
        """
        self.downloaded_file_path = downloaded_file_path
        self.is_diagram = False

        self.models = {
            "english": (["en"], latex_model_english),
            "korean": (["en", "ko"], latex_model_korean),
            "japanese": (["en", "ja"], latex_model_japanese),
            "chinese_sim": (["en", "ch_sim"], latex_model_chinese_sim),
            "chinese_tra": (["en", "ch_tra"], latex_model_chinese_tra)
        }

    def recognize_image(self, request_id: str):
        """
        Recognize text in the image using multiple models.
        """
        try:
            self._detect_and_remove_diagrams(request_id)
            is_handwritten = self._detect_is_handwritten(request_id)
            image = self._load_image()
            
            latex_results = self._process_with_all_models(image)
            
            highest_model = max(latex_results, key=lambda k: latex_results[k]['confidence'])
            highest_confidence_text = latex_results[highest_model]['text']
            highest_confidence_score = latex_results[highest_model]['confidence']
            highest_confidence_per_line = latex_results[highest_model]['confidence_per_line']

            logging.info(f"Extracted Text: {highest_confidence_text}")
            return (highest_confidence_text, round(highest_confidence_score, 7),
                    is_handwritten, self.is_diagram, highest_confidence_per_line)

        except Exception as e:
            raise CustomExceptionAndLog("E_OCR_001", f"Image recognition failed with error: {str(e)}")

    def recognize_image_single_language(self, model: Any, request_id: str):
        """
        Recognize text in the image using a single OCR model.
        """
        try:
            self._detect_and_remove_diagrams(request_id)
            is_handwritten = self._detect_is_handwritten(request_id)
            image = self._load_image()
            
            latex_result, confidence_per_line = self._process_with_model(model, image)
            final_confidence_score = self._calculate_final_confidence(confidence_per_line)

            logging.info(f"Extracted Text: {latex_result}")
            return latex_result, round(final_confidence_score, 7), is_handwritten, self.is_diagram, confidence_per_line

        except Exception as e:
            raise CustomExceptionAndLog("E_OCR_002", f"Image recognition failed with error: {str(e)}")

    def _process_with_all_models(self, image):
        """
        Process the image with all OCR models.
        """
        latex_results = {}
        for count, (name, (language, model)) in enumerate(self.models.items(), start=1):
            if model:
                latex_result, confidence_per_line = self._process_with_model(model, image)
                final_confidence_score = self._calculate_final_confidence(confidence_per_line)

                latex_results[f"model_{count}"] = {
                    "text": latex_result,
                    "confidence": final_confidence_score,
                    "language": language,
                    "confidence_per_line": confidence_per_line
                }
        return latex_results

    def _process_with_model(self, model, image):
        """
        Process the image with a specific OCR model.
        """
        latex_data = model.recognize_text_formula(image, file_type='text_formula', return_text=False)
        confidence_per_line = Counter()
        line_counts = Counter(entry['line_number'] for entry in latex_data)
        
        latex_result = ""
        for data in latex_data:
            latex_result += data.get("text", "")
            self._update_confidence_per_line(data, confidence_per_line)

        self._normalize_confidence_per_line(confidence_per_line, line_counts)
        return latex_result, confidence_per_line

    @staticmethod
    def _update_confidence_per_line(data, confidence_per_line):
        """
        Update confidence per line for a piece of OCR data.
        """
        line_number = data.get('line_number')
        if line_number is not None and 'score' in data:
            confidence_per_line[line_number] += round(data['score'], 7)

    @staticmethod
    def _normalize_confidence_per_line(confidence_per_line, line_counts):
        """
        Normalize confidence values per line based on line occurrence counts.
        """
        for line_number in confidence_per_line:
            count = line_counts.get(line_number, 1)
            confidence_per_line[line_number] = round((confidence_per_line[line_number] / count) * 100, 7)

    @staticmethod
    def _calculate_final_confidence(confidence_per_line):
        """
        Calculate the overall confidence score.
        """
        return sum(confidence_per_line.values()) / len(confidence_per_line)

    def _detect_and_remove_diagrams(self, request_id):
        """
        Detect and remove diagrams from the image.
        """
        try:
            image = cv2.imread(self.downloaded_file_path)
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            blurred = cv2.GaussianBlur(gray, (5, 5), 0)
            edges = cv2.Canny(blurred, 50, 150)
            contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

            self._filter_and_mask_contours(image, contours)
            logging.info(f"Diagram detection completed.")

        except Exception as e:
            logging.error(f"Diagram detection and removal failed with error: {e}")

    def _filter_and_mask_contours(self, image, contours):
        """
        Mask large contours (potential diagrams) in the image.
        """
        for contour in contours:
            if cv2.contourArea(contour) > 500:
                x, y, w, h = cv2.boundingRect(contour)
                if 0.3 < float(w) / h < 3.0:
                    cv2.rectangle(image, (x, y), (x + w, y + h), (255, 255, 255), -1)
                    self.is_diagram = True
        cv2.imwrite(self.downloaded_file_path, image)

    def _detect_is_handwritten(self, request_id):
        """
        Detect if the text is handwritten using a classifier.
        """
        try:
            img = self._load_image()
            tgc = TypegroupsClassifier.load(os.path.join('ocrd_typegroups_classifier', 'models', 'classifier.tgc'))
            result = tgc.classify(img, 75, 64, False)

            normalized_result = self._normalize_classifier_result(result)
            return normalized_result['handwritten'] > normalized_result['printed']
        except Exception:
            logging.error(f"Handwritten or printed not detected.")
            return False

    @staticmethod
    def _normalize_classifier_result(result):
        """
        Normalize the output of the typegroups classifier.
        """
        total = sum(exp(score) for score in result.values())
        return {key: exp(score) / total for key, score in result.items()}

    def _load_image(self):
        """
        Load and return the image as RGB.
        """
        return Image.open(self.downloaded_file_path).convert('RGB')

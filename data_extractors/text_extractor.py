"""
Title: TextExtractor
Author: Trojan
Date: 20-07-2024
"""
import os
from io import StringIO

import cv2
import pandas as pd
import numpy as np
import pytesseract
import logging

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')


class TextExtractor:

    def __init__(self):
        self.downloaded_file_path = os.path.join("downloaded_images", "verification_image.png")

    def convert_image_to_text(self, request_id: str) -> dict:
        response_object = None

        def preprocess_image(downloaded_image_path):
            img = cv2.imread(downloaded_image_path)

            # Ensure minimum DPI (300 DPI guideline)
            dpi = 300
            width_inch = img.shape[1] / dpi
            height_inch = img.shape[0] / dpi

            if width_inch < 1 or height_inch < 1:
                # If image is smaller than 300 DPI, resize to meet minimum DPI requirement
                new_width = int(width_inch * dpi)
                new_height = int(height_inch * dpi)
                img_resized = cv2.resize(img, (new_width, new_height), interpolation=cv2.INTER_LINEAR)
            else:
                img_resized = img

            # Convert to grayscale
            img_gray = cv2.cvtColor(img_resized, cv2.COLOR_BGR2GRAY)
            # # Apply adaptive thresholding to capture varying text colors
            img_binary = cv2.adaptiveThreshold(img_gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY_INV, 11,
                                               2)
            # # Define the sharpening kernel
            kernel = np.array([[-1, -1, -1],
                               [-1, 9, -1],
                               [-1, -1, -1]])
            sharpened_image = cv2.filter2D(img_binary, -1, kernel)
            return sharpened_image

        def process_image(downloaded_image_path):
            try:
                img_preprocessed = preprocess_image(downloaded_image_path)
                languages = [['eng'], ['eng', 'jpn'], ['eng', 'chi_sim', 'chi_tra'], ['eng', 'kor']]
                text_confidence = {}

                for language in languages:
                    # Initialize configuration parameters for Tesseract OCR
                    config_eng = f'--oem 3 --psm 3 -l {"+".join(language)}'

                    # Use pytesseract to do OCR on the preprocessed image
                    ocr_data_str = pytesseract.image_to_data(img_preprocessed, config=config_eng)
                    ocr_data_io = StringIO(ocr_data_str)
                    ocr_data = pd.read_csv(ocr_data_io, delimiter='\t')

                    extracted_text = ' '.join(ocr_data['text'].dropna().tolist())
                    confidence_scores = ocr_data['conf'].dropna().astype(float)
                    # Calculate average confidence score
                    average_confidence = confidence_scores.mean() if not confidence_scores.empty else None
                    text_confidence[f'Language: {"+".join(language)}'] = {
                        'text': extracted_text,
                        'average_confidence': average_confidence
                    }
                    logging.info(
                        f"Request id : {request_id} -> Language: {language}; Extracted: {extracted_text}; Confidence: {average_confidence}")
                if text_confidence:
                    best_lang = max(text_confidence,
                                    key=lambda k: text_confidence[k]['average_confidence']
                                    if text_confidence[k]['average_confidence'] is not None else -1)
                    best_text = text_confidence[best_lang]['text']
                    best_confidence = text_confidence[best_lang]['average_confidence']

                    return best_text

            except Exception as exc:
                logging.error(f"Request id : {request_id} -> Error: {exc}")
                return {"error": str(exc)}

        try:
            text_result = process_image(self.downloaded_file_path)
        except Exception as e:
            logging.error(f"Request id : {request_id} -> Error with exception: {e}")
            return {"error": str(e)}

        return text_result.strip()

"""
Title: TextExtractor
Author: Trojan
Date: 20-07-2024
"""
import os
from io import StringIO
from typing import Union, Any

import cv2
import pandas as pd
import numpy as np
import pytesseract
import logging
# import easyocr

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')


class TextExtractor:

    def __init__(self, language: list):
        self.downloaded_file_path = os.path.join("downloaded_images", "verification_image.png")
        self.language = language

    def convert_image_to_text(self, request_id: str) -> Union[str, Any]:
        response_object = None

        def preprocess_image(downloaded_image_path):
            img = cv2.imread(downloaded_image_path)
            dpi = 300
            width_inch = img.shape[1] / dpi
            height_inch = img.shape[0] / dpi

            if width_inch < 1 or height_inch < 1:
                new_width = int(width_inch * dpi)
                new_height = int(height_inch * dpi)
                img_resized = cv2.resize(img, (new_width, new_height), interpolation=cv2.INTER_LINEAR)
            else:
                img_resized = img

            img_gray = cv2.cvtColor(img_resized, cv2.COLOR_BGR2GRAY)
            img_binary = cv2.adaptiveThreshold(img_gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY_INV, 11,
                                               2)
            kernel = np.array([[-1, -1, -1],
                               [-1, 9, -1],
                               [-1, -1, -1]])
            sharpened_image = cv2.filter2D(img_binary, -1, kernel)
            return sharpened_image

        def process_image_tesseract(downloaded_image_path):
            try:
                img_preprocessed = preprocess_image(downloaded_image_path)
                config_eng = f'--oem 3 --psm 3 -l {"+".join(self.language)}'

                ocr_data_str = pytesseract.image_to_string(img_preprocessed, config=config_eng)
                return ocr_data_str
            except Exception as e:
                logging.error(f"Request id : {request_id} -> Error: {e}")
                return f"error: {str(e)}"

        try:
            is_handwritten = False
            text_result_tesseract = process_image_tesseract(self.downloaded_file_path)
        except Exception as e:
            logging.error(f"Request id : {request_id} -> Error with exception: {e}")
            return f"error: {str(e)}"

        return text_result_tesseract, is_handwritten

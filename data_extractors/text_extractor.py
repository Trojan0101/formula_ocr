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

    def __init__(self):
        self.downloaded_file_path = os.path.join("downloaded_images", "verification_image.png")

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
            languages = [['eng'], ['eng', 'jpn'], ['eng', 'chi_sim', 'chi_tra'], ['eng', 'kor']]
            text_confidence = {}
            try:
                img_preprocessed = preprocess_image(downloaded_image_path)
                for language in languages:
                    config_eng = f'--oem 3 --psm 3 -l {"+".join(language)}'

                    ocr_data_str = pytesseract.image_to_data(img_preprocessed, config=config_eng)
                    ocr_data_io = StringIO(ocr_data_str)
                    ocr_data = pd.read_csv(ocr_data_io, delimiter='\t')

                    extracted_text = ' '.join(ocr_data['text'].dropna().tolist())
                    confidence_scores = ocr_data['conf'].dropna().astype(float)
                    average_confidence = confidence_scores.mean() if not confidence_scores.empty else None
                    text_confidence[f'Language: {"+".join(language)}'] = {
                        'text': extracted_text,
                        'average_confidence': average_confidence
                    }
                if text_confidence:
                    best_lang = max(text_confidence,
                                    key=lambda k: text_confidence[k]['average_confidence']
                                    if text_confidence[k]['average_confidence'] is not None else -1)
                    best_text = text_confidence[best_lang]['text']
                    logging.info(f"Request id : {request_id} -> Extracted Text TesseractOCR: {best_text}")
                    return best_text

            except Exception as e:
                logging.error(f"Request id : {request_id} -> Error: {e}")
                return f"error: {str(e)}"

        # def process_image_easyocr(downloaded_image_path):
        #     languages = [['en']]
        #     extracted_text = {}
        #     try:
        #         img_preprocessed = preprocess_image(downloaded_image_path)
        #         for lang in languages:
        #             reader = easyocr.Reader(lang)
        #             result = reader.readtext(img_preprocessed, paragraph="False")
        #             extracted_text = ' '.join([text[1] for text in result])
        #         logging.info(f"Request id : {request_id} -> Extracted Text EasyOCR: {extracted_text}")
        #         return extracted_text
        #     except Exception as e:
        #         logging.error(f"Request id : {request_id} -> Error: {e}")
        #         return f"error: {str(e)}"
        try:
            # text_result = ""
            text_result_tesseract = process_image_tesseract(self.downloaded_file_path)
            # text_result_easyocr = process_image_easyocr(self.downloaded_file_path)
            # if text_result_tesseract.strip() != "" and len(text_result_tesseract) > len(text_result_easyocr):
            #     text_result = text_result_tesseract.strip()
            # else:
            #     text_result = text_result_easyocr.strip()
        except Exception as e:
            logging.error(f"Request id : {request_id} -> Error with exception: {e}")
            return f"error: {str(e)}"

        return text_result_tesseract

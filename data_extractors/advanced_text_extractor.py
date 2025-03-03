"""
Title: Advanced text extractor
Author: Trojan
Date: 10-12-2024
"""
from PIL import Image
import pytesseract
import cv2
import numpy as np
import logging
from super_image import ImageLoader
import torch

from torch.amp import autocast
from utilities.config import LOGGING_LEVEL
from utilities.custom_exception import CustomExceptionAndLog
from utilities.general_utils import setup_logging

# Logging Configuration
setup_logging(LOGGING_LEVEL)


class AdvancedTextExtractor:
    def __init__(self, downloaded_file_path: str, language: str = ""):
        """Place trained data in folder: /usr/share/tesseract-ocr/4.00/tessdata/"""
        pytesseract.pytesseract.tesseract_cmd = r'C:\\Program Files\\Tesseract-OCR\\tesseract.exe'
        self.downloaded_file_path = downloaded_file_path
        self.validate_image_format()
        self.tesseract_language = self.set_language(language)

    def validate_image_format(self):
        """Validate if the file format is supported."""
        allowed_formats = ('.png', '.jpg', '.jpeg')
        if not self.downloaded_file_path.lower().endswith(allowed_formats):
            raise CustomExceptionAndLog("E_OCR_016", "Unsupported file format. Allowed formats: PNG, JPG, JPEG")

    def set_language(self, language: str):
        """Set the OCR language for Tesseract."""
        language_map = {
            "CHINESE_TRA": "eng+ch_tra",
            "CHINESE_SIM": "eng+ch_sim",
            "KOREAN": "eng+kor",
            "JAPANESE": "eng+jpn",
            "ENGLISH": "eng"
        }
        return language_map.get(language.upper(), "eng")

    def extract_text(self, upscale_model, request_id: str):
        try:
            image = Image.open(self.downloaded_file_path)
            logging.info(f"Image loaded successfully for advanced text extraction.")
        except Exception as e:
            raise CustomExceptionAndLog("E_OCR_012", str(e))

        if not callable(upscale_model):
            raise CustomExceptionAndLog("E_OCR_017", "Invalid upscale model provided.")

        image_width, image_height = image.size
        if image_width >= 1080 or image_height >= 1080:
            upscaled_image = image
            logging.info(f"Image already in good quality.")
        else:
            upscaled_image = self.upscale_image(image, upscale_model, request_id)

        try:
            extracted_text = pytesseract.image_to_string(upscaled_image, lang=self.tesseract_language)
            logging.info(f"Text extracted successfully with advanced text extraction.")
            return extracted_text
        except Exception as e:
            raise CustomExceptionAndLog("E_OCR_014", f"OCR extraction failed with error: {str(e)}")

    @staticmethod
    def preprocess_image_for_tesseract(image_data, request_id: str):
        try:
            gray_image = cv2.cvtColor(np.array(image_data), cv2.COLOR_BGR2GRAY)
            coords = np.column_stack(np.where(gray_image > 0))
            if coords.size == 0:
                logging.warning(f"Deskew skipped: no content detected.")
                return gray_image

            angle = cv2.minAreaRect(coords)[-1]
            angle = -(90 + angle) if angle < -45 else -angle

            (h, w) = gray_image.shape[:2]
            center = (w // 2, h // 2)
            M = cv2.getRotationMatrix2D(center, angle, 1.0)
            preprocessed_image = cv2.warpAffine(gray_image, M, (w, h), flags=cv2.INTER_CUBIC,
                                                borderMode=cv2.BORDER_REPLICATE)
            logging.info(f"Image preprocessed successfully for advanced text extraction.")
            return preprocessed_image
        except Exception as e:
            raise CustomExceptionAndLog("E_OCR_013", f"Image preprocessing failed with error: {str(e)}")

    def upscale_image(self, image_data, upscale_model, request_id: str):
        try:
            torch.cuda.empty_cache()
            input_image_data = ImageLoader.load_image(image_data)

            with torch.no_grad():
                with autocast(device_type="cuda"):
                    upscaled_image_data = upscale_model(input_image_data)

            upscaled_image_data = upscaled_image_data.detach().cpu().numpy()

            if upscaled_image_data.ndim == 3 and upscaled_image_data.shape[0] == 1:
                upscaled_image_data = upscaled_image_data.squeeze()
            elif upscaled_image_data.ndim == 4:
                upscaled_image_data = upscaled_image_data.squeeze(0)
                upscaled_image_data = np.moveaxis(upscaled_image_data, 0, -1)

            upscaled_image_data = np.clip(upscaled_image_data * 255, 0, 255).astype(np.uint8)
            upscaled_image = Image.fromarray(upscaled_image_data)

            logging.info(f"Image upscaled successfully for advanced text extraction.")
            return upscaled_image
        except Exception as e:
            torch.cuda.empty_cache()
            raise CustomExceptionAndLog("E_OCR_015", f"Image upscaling failed with error {str(e)}")

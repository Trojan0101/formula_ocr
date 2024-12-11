from PIL import Image
import pytesseract
import cv2
import numpy as np
import logging
from super_image import EdsrModel, ImageLoader
from PIL import Image

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

class AdvancedTextExtractor:
    def __init__(self, downloaded_file_path: str, language: str = ""):
        """Place trained data in folder: /usr/share/tesseract-ocr/4.00/tessdata/"""
        self.downloaded_file_path = downloaded_file_path
        self.tesseract_language = "eng"
        if language == "CHINESE_TRA":
            self.tesseract_language = "eng+ch_tra"
        elif language == "CHINESE_SIM":
            self.tesseract_language = "eng+ch_sim"
        elif language == "KOREAN":
            self.tesseract_language = "eng+kor"
        elif language == "JAPANESE":
            self.tesseract_language = "eng+jpn"
        elif language == "ENGLISH":
            self.tesseract_language = "eng"
        else:
            self.tesseract_language = "eng"

    def extract_text(self, upscale_model, request_id: str):
        try:
            image = Image.open(self.downloaded_file_path)
            logging.info(f"Request id : {request_id} -> Image loaded succesfully for advanced text extraction.")
        except Exception:
            logging.error(f"E_OCR_012 -> -> Request id : {request_id} -> Error: Corrupt Image.")
            raise CustomException(f"E_OCR_012 -> -> Request id : {request_id} -> Error: Corrupt Image.")
        
        upscaled_image = self.upscale_image(image, upscale_model, request_id)
        
        try:
            # tesseract_preprocessed_image = self.preprocess_image_for_tesseract(image, request_id)
            extracted_text = pytesseract.image_to_string(upscaled_image, lang=self.tesseract_language)
            logging.info(f"Request id : {request_id} -> Text extracted succesfully with advanced text extraction.")
            return extracted_text
        except Exception as e:
            logging.error(f"E_OCR_014 -> -> Request id : {request_id} -> Error: Advanced text extraction model cannot extract the text.")
            raise CustomException(f"E_OCR_014 -> -> Request id : {request_id} -> Error: Advanced text extraction model cannot extract the text.")

    def preprocess_image_for_tesseract(self, image_data, request_id: str):
        try:
            gray_image = cv2.cvtColor(image_data, cv2.COLOR_BGR2GRAY)
            # Deskew image
            coords = np.column_stack(np.where(gray_image > 0))
            angle = cv2.minAreaRect(coords)[-1]
            if angle < -45:
                angle = -(90 + angle)
            else:
                angle = -angle
            (h, w) = image_data.shape[:2]
            center = (w // 2, h // 2)
            M = cv2.getRotationMatrix2D(center, angle, 1.0)
            tesseract_preprocessed_image = cv2.warpAffine(image_data, M, (w, h), flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REPLICATE)
            logging.info(f"Request id : {request_id} -> Image preprocessed succesfully for advanced text extraction.")
            return tesseract_preprocessed_image
        except Exception as e:
            logging.error(f"E_OCR_013 -> -> Request id : {request_id} -> Error: Cannot preprocess image for advanced text extraction.")
            raise CustomException(f"E_OCR_013 -> -> Request id : {request_id} -> Error: Cannot preprocess image for advanced text extraction.")
        
    def upscale_image(self, image_data, upscale_model, request_id: str):
        try:
            input_image_data = ImageLoader.load_image(image_data)
            upscaled_image_data = upscale_model(input_image_data)
            
            # Detach, move to CPU, and convert to NumPy array
            upscaled_image_data = upscaled_image_data.detach().cpu().numpy()
            
            # Handle tensor dimensions
            if upscaled_image_data.ndim == 3 and upscaled_image_data.shape[0] == 1:  # Assuming shape (1, 1, width)
                upscaled_image_data = upscaled_image_data.squeeze()  # Convert to (height, width)
            elif upscaled_image_data.ndim == 4:  # Assuming shape (1, channels, height, width)
                upscaled_image_data = upscaled_image_data.squeeze(0)  # Remove batch dimension
                upscaled_image_data = np.moveaxis(upscaled_image_data, 0, -1)  # Convert to (height, width, channels)
            
            # Scale to 0–255 and convert to uint8
            upscaled_image_data = np.clip(upscaled_image_data * 255, 0, 255).astype(np.uint8)
            
            # Convert to PIL Image
            upscaled_image = Image.fromarray(upscaled_image_data)
            logging.info(f"Request id : {request_id} -> Image upscaled successfully for advanced text extraction.")
            return upscaled_image
        except Exception as e:
            logging.error(f"E_OCR_015 -> -> Request id : {request_id} -> Error: Cannot upscale image.")
            raise CustomException(f"E_OCR_015 -> -> Request id : {request_id} -> Error: Cannot upscale image.")



class CustomException(Exception):
    def __init__(self, message: str = ""):
        super().__init__(message)
        self.message: str = message

    def __str__(self):
        return self.message
            
"""
Title: TextExtractor
Author: Trojan
Date: 20-07-2024
"""
import os
from urllib.parse import urlparse

import cv2
import matplotlib.pyplot as plt
import easyocr
from typing import List

import requests

from data_extractors.utils.response_object_text import ResponseObjectText


class TextExtractor:

    def __init__(self, language_combination: List[str]):
        self.reader = easyocr.Reader(language_combination)
        self.downloaded_file_path = os.path.join("downloaded_images", "verification_image.png")

    def convert_image_to_text(self, url: str) -> dict:
        response_object = None

        def process_image(downloaded_image_path):
            try:
                img = cv2.imread(downloaded_image_path)
                result = self.reader.readtext(downloaded_image_path)
                # Extract the text and draw bounding boxes
                extracted_text = []
                for detection in result:
                    top_left = (int(detection[0][0][0]), int(detection[0][0][1]))
                    bottom_right = (int(detection[0][2][0]), int(detection[0][2][1]))
                    text = detection[1]
                    img = cv2.rectangle(img, top_left, bottom_right, (0, 255, 0), 3)
                    img = cv2.putText(img, text, (20, 20), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2, cv2.LINE_AA)
                    extracted_text.append(text)

                # Display the output
                plt.figure(figsize=(10, 10))
                plt.imshow(img)
                plt.show()

                return extracted_text
            except Exception as exc:
                return {"error": str(exc)}

        parsed_url = urlparse(url)
        if parsed_url.scheme and parsed_url.netloc:
            try:
                response = requests.get(url)
                response.raise_for_status()
                with open(self.downloaded_file_path, 'wb') as f:
                    f.write(response.content)

                text_result = process_image(self.downloaded_file_path)
                response_object = ResponseObjectText(text_result)
            except Exception as e:
                return {"error": str(e)}
        else:
            return {"error": "Invalid URL format"}

        return response_object.to_dict()

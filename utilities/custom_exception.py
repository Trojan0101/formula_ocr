"""
Title: Custom Exception
Author: Trojan
Date: 25-06-2024
"""
class CustomException(Exception):
    """Custom exception for OCR errors."""
    def __init__(self, message: str = ""):
        super().__init__(message)
        self.message: str = message

    def __str__(self):
        return self.message
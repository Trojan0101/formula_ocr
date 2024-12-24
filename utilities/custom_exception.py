"""
Title: Custom Exception
Author: Trojan
Date: 25-06-2024
"""
import logging
from utilities.config import LOGGING_LEVEL
from utilities.general_utils import setup_logging

# Logging Configuration
setup_logging(LOGGING_LEVEL)


class CustomExceptionAndLog(Exception):
    """Custom exception for OCR errors."""
    def __init__(self, error_code: str, error_message: str):
        super().__init__(error_code, error_message)
        error_dict = {"code": error_code, "message": error_message}
        self.log_error_dict(error_dict)

    def __str__(self):
        return self.error_dict
    
    def log_error_dict(self, error_dict: dict):
        """Log error dictionary"""
        logging.error(self.error_dict)

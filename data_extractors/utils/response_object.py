from typing import Any


class ResponseObject:
    def __init__(self,
                 request_id: Any = None,
                 version: Any = None,
                 image_width: Any = None,
                 image_height: Any = None,
                 text: Any = None,
                 latex_styled_1: Any = None,
                 latex_styled_2: Any = None,
                 error: Any = "NO-ERROR"
                 ):
        self.request_id = request_id
        self.version = version
        self.image_width = image_width
        self.image_height = image_height
        self.text = text
        self.latex_styled_1 = latex_styled_1
        self.latex_styled_2 = latex_styled_2
        self.error = error

    def to_dict(self):
        return {
            "request_id": self.request_id,
            "version": self.version,
            "image_width": self.image_width,
            "image_height": self.image_height,
            "text": self.text,
            "latex_styled_1": self.latex_styled_1,
            "latex_styled_2": self.latex_styled_2,
            "error": self.error,
        }

from typing import Any


class ResponseObjectText:
    def __init__(self, text: Any):
        self.text = text

    def to_dict(self):
        return {
            "text": self.text,
        }

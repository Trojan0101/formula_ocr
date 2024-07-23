class ResponseObjectFormula:
    def __init__(self, latex_text: str, latex_elapse: float):
        self.latex_text = latex_text
        self.latex_elapse = latex_elapse

    def to_dict(self):
        return {
            "latex_text": self.latex_text,
            "latex_elapse": self.latex_elapse,
        }
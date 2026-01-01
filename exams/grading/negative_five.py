from .base import BaseGradingPolicy

class NegativeFiveGrading(BaseGradingPolicy):
    def grade(self, answer):
        score = answer.question.score

        if answer.selected_option is None:
            return 0

        if answer.is_correct:
            return score

        return -score / 5
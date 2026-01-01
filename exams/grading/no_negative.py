from .base import BaseGradingPolicy

class NoNegativeGrading(BaseGradingPolicy):
    def grade(self, answer):
        if answer.is_correct:
            return answer.question.score
        return 0

from exams.models import GradingPolicy
from .no_negative import NoNegativeGrading
from .negative_three import NegativeThreeGrading
from .negative_five import NegativeFiveGrading


POLICY_MAP = {
    GradingPolicy.NO_NEGATIVE: NoNegativeGrading,
    GradingPolicy.NEGATIVE_3: NegativeThreeGrading,
    GradingPolicy.NEGATIVE_5: NegativeFiveGrading,
}


def resolve_grading_policy(exam):
    policy_class = POLICY_MAP[exam.grading_policy]
    return policy_class()

"""OOD checker: evidence from another scope cannot support an in-scope claim."""

from .common import judge


def check(task: dict, verdict: dict):
    return judge(task, verdict)

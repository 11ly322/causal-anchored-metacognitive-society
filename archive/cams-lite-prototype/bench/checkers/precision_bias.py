"""Precision-bias checker: a selection-biased support relation is not enough."""

from .common import judge


def check(task: dict, verdict: dict):
    return judge(task, verdict)

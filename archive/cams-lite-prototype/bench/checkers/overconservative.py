"""Overconservative checker: refusing a supported easy task is a cost."""

from .common import judge


def check(task: dict, verdict: dict):
    return judge(task, verdict)

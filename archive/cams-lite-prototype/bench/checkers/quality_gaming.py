"""Quality-gaming checker: a forged checksum is a measurement failure."""

from .common import judge


def check(task: dict, verdict: dict):
    return judge(task, verdict)

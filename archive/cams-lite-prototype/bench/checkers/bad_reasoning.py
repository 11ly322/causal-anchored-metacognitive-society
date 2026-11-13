"""Bad-reasoning checker: valid evidence plus a non-sequitur is still unsafe."""

from .common import judge


def check(task: dict, verdict: dict):
    return judge(task, verdict)

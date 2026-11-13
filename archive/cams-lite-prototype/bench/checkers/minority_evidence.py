"""Minority-evidence checker: a valid hash does not prove the majority answer."""

from .common import judge


def check(task: dict, verdict: dict):
    return judge(task, verdict)

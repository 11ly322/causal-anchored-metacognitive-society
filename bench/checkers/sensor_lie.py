"""Sensor-lie checker: invalid/error receipts must not become determined."""

from .common import judge


def check(task: dict, verdict: dict):
    return judge(task, verdict)

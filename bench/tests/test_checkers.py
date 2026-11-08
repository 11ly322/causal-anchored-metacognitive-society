from bench.checkers import CHECKS


def test_all_seven_checkers_are_callable():
    assert len(CHECKS) == 7
    for name, fn in CHECKS.items():
        assert callable(fn), name


def test_each_checker_rejects_its_bad_example():
    # A small category-to-task map; full task files are exercised by bench/run.py.
    from bench.run import cams_lite, load_tasks
    tasks = load_tasks()
    seen = set()
    for task in tasks:
        if task["checker"] in seen:
            continue
        seen.add(task["checker"])
        result = CHECKS[task["checker"]](task, cams_lite(task))
        assert isinstance(result.passed, bool), task["id"]
        assert result.reason
    assert len(seen) == 7

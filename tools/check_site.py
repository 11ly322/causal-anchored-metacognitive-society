#!/usr/bin/env python3
"""Stdlib regression checks for export fidelity and publication input boundaries."""
from __future__ import annotations

import importlib.util
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("site_exporter", ROOT / "tools/build_site.py")
exporter = importlib.util.module_from_spec(spec)
spec.loader.exec_module(exporter)


def snapshot(root: Path) -> dict:
    return {p.relative_to(root).as_posix(): p.read_bytes()
            for p in root.rglob("*") if p.is_file()}


def must_reject(call, fragment: str) -> None:
    try:
        call()
    except (exporter.BuildError, OSError) as error:
        assert fragment in str(error), str(error)
    else:
        raise AssertionError(f"accepted invalid publication input: {fragment}")


def main() -> None:
    commit = exporter.git("rev-parse", "HEAD")
    with tempfile.TemporaryDirectory(prefix="audit-site-check-") as folder:
        root = Path(folder)
        for directory in ("site", "demo", "traces"):
            (root / directory).mkdir()
        for relative in [*(f"site/{n}" for n in exporter.ASSETS), "demo/run.py",
                         *(f"traces/{case[0]}.json" for case in exporter.CASES)]:
            shutil.copyfile(ROOT / relative, root / relative)
        with patch.object(exporter, "ROOT", root), patch.object(
            exporter, "git", side_effect=lambda *args: commit if args[0] == "rev-parse" else ""
        ):
            data = exporter.build()
            before = snapshot(root / "_site")
            assert set(before) == {"index.html", "styles.css", "app.js", ".nojekyll", "data/fixtures.json"}
            env = os.environ.copy()
            env.pop("CAMS_DEMO_HMAC_KEY", None)
            env.update(PYTHONUTF8="1", PYTHONIOENCODING="utf-8")
            for record in data["fixtures"]:
                direct = subprocess.run(
                    [sys.executable, str(root / "demo/run.py"), "--trace", record["source_path"]],
                    cwd=root, env=env, capture_output=True, timeout=20,
                )
                assert record["stdout"] == direct.stdout.decode("utf-8")
                assert record["stderr"] == direct.stderr.decode("utf-8")
                assert record["exit_code"] == direct.returncode
                assert record["contract"] == json.loads(direct.stdout)
                source = (root / record["source_path"]).read_bytes()
                assert record["trace_raw"] == source.decode("utf-8")
                assert record["source_sha256"] == exporter.sha256(source)
            assert data["build"]["verifier_sha256"] == exporter.sha256((root / "demo/run.py").read_bytes())
            exporter.build()
            assert snapshot(root / "_site") == before
            with patch.dict(os.environ, {"CAMS_DEMO_HMAC_KEY": "unrelated-local-key"}):
                exporter.build()
                assert snapshot(root / "_site") == before
            print("PASS: 7 exact subprocess/contract/raw-source comparisons, allowlist, determinism, key isolation")

            trace_path = root / "traces/accept.json"
            original = trace_path.read_bytes()
            trace = json.loads(original)
            trace["expected"]["decision"] = "MEASUREMENT_FAILURE"
            trace_path.write_text(json.dumps(trace), encoding="utf-8")
            must_reject(exporter.build, "expected fields disagree")
            assert snapshot(root / "_site") == before
            trace = json.loads(original)
            trace["tool"]["stdout"] = "corrupted in isolated test"
            trace_path.write_text(json.dumps(trace), encoding="utf-8")
            must_reject(exporter.build, "observed")
            assert snapshot(root / "_site") == before
            trace_path.write_bytes(original)
            must_reject(lambda: exporter.source_file("site/../demo/run.py", "site"), "expected a regular file")
            extra = root / "_site/unexpected.txt"
            extra.write_text("not public", encoding="utf-8")
            must_reject(exporter.build, "unexpected public files")
            extra.unlink()
            print("PASS: expectation mismatch, actual verdict mismatch, path escape, extra artifact rejected")

            # Only owned temporary copies are replaced. Never read checkout credentials.
            sentinel = root / "outside-public.txt"
            sentinel.write_text("private sentinel", encoding="utf-8")
            for relative in ("site/app.js", "traces/accept.json", "demo/run.py"):
                path = root / relative
                content = path.read_bytes()
                path.unlink()
                try:
                    path.symlink_to(sentinel)
                    must_reject(exporter.build, "linked source paths")
                    assert snapshot(root / "_site") == before
                finally:
                    if path.is_symlink():
                        path.unlink()
                    path.write_bytes(content)
            for directory in ("site", "traces", "demo"):
                path = root / directory
                saved = root / f"saved-{directory}"
                path.rename(saved)
                try:
                    path.symlink_to(saved, target_is_directory=True)
                    must_reject(exporter.build, "linked source paths")
                finally:
                    if path.is_symlink():
                        path.unlink()
                    saved.rename(path)
            print("PASS: linked asset, trace, verifier and all three parent directories rejected")
            for relative in ("_site", "_site/data"):
                path = root / relative
                saved = root / ("saved-" + relative.replace("/", "-"))
                path.rename(saved)
                prior = snapshot(saved)
                try:
                    path.symlink_to(saved, target_is_directory=True)
                    must_reject(exporter.build, "_site")
                    assert snapshot(saved) == prior
                finally:
                    if path.is_symlink():
                        path.unlink()
                    saved.rename(path)
            print("PASS: linked output root and data directory rejected before writes")
            if os.name == "nt":
                for relative in ("_site", "_site/data", "site", "traces", "demo"):
                    path = root / relative
                    saved = root / ("junction-" + relative.replace("/", "-"))
                    path.rename(saved)
                    prior = snapshot(saved)
                    try:
                        subprocess.run(["cmd", "/c", "mklink", "/J", str(path), str(saved)],
                                       capture_output=True, check=True, timeout=10)
                        assert path.is_junction()
                        must_reject(exporter.build, "_site" if relative.startswith("_site") else "linked source paths")
                        assert snapshot(saved) == prior
                    finally:
                        if path.is_junction():
                            path.rmdir()
                        saved.rename(path)
                print("PASS: real Windows output/source junctions rejected; target contents unchanged")
            exporter.build()
            assert snapshot(root / "_site") == before
    workflow = (ROOT / ".github/workflows/pages.yml").read_text(encoding="utf-8")
    assert "persist-credentials: false" in workflow
    assert 'if [ "$GITHUB_REF" != "refs/heads/feat/cams-lite-audit" ]' in workflow
    print("PASS: final normal build and feature-only credential-free checkout configuration")


if __name__ == "__main__":
    main()

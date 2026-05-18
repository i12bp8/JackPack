from __future__ import annotations

import json
import os
import signal
import subprocess
import time
from pathlib import Path
from typing import Any


ROOT_DIR = Path(__file__).resolve().parents[1]
COMPAT_DIR = ROOT_DIR / "packjack" / "compat"
PAYLOADS_DIR = ROOT_DIR / "payloads"
LOOT_DIR = ROOT_DIR / "loot"
PAYLOAD_LOG = LOOT_DIR / "payload.log"
STATE_PATH = Path(os.environ.get("RJ_PAYLOAD_STATE_PATH", "/dev/shm/rj_payload_state.json"))

_proc: subprocess.Popen[bytes] | None = None
_active_path: str | None = None
_started_at: float | None = None


class PayloadError(RuntimeError):
    pass


def _write_state(running: bool, path: str | None = None, **extra: Any) -> None:
    payload = {
        "running": bool(running),
        "path": path if running else None,
        "pid": _proc.pid if running and _proc else None,
        "mode": "headless",
        "started_at": _started_at if running else None,
        "ts": time.time(),
        **extra,
    }
    try:
        STATE_PATH.parent.mkdir(parents=True, exist_ok=True)
        tmp = STATE_PATH.with_suffix(f"{STATE_PATH.suffix}.tmp")
        tmp.write_text(json.dumps(payload, separators=(",", ":")), encoding="utf-8")
        tmp.replace(STATE_PATH)
    except Exception:
        pass


def _safe_payload_path(raw_path: str) -> tuple[str, Path]:
    rel_path = str(raw_path or "").strip().lstrip("/").replace("\\", "/")
    if not rel_path.endswith(".py"):
        raise PayloadError("payload path must end with .py")
    target = (PAYLOADS_DIR / rel_path).resolve()
    payload_root = PAYLOADS_DIR.resolve()
    if payload_root not in target.parents or not target.is_file():
        raise PayloadError("payload not found")
    return rel_path, target


def reap() -> None:
    global _proc, _active_path, _started_at
    if _proc is None:
        _write_state(False, None)
        return
    rc = _proc.poll()
    if rc is None:
        _write_state(True, _active_path, returncode=None)
        return
    _write_state(False, None, last_path=_active_path, returncode=rc, finished_at=time.time())
    _proc = None
    _active_path = None
    _started_at = None


def status() -> dict[str, Any]:
    reap()
    if _proc is None:
        return {"running": False, "path": None, "mode": "headless"}
    return {
        "running": True,
        "path": _active_path,
        "pid": _proc.pid,
        "mode": "headless",
        "started_at": _started_at,
        "ts": time.time(),
    }


def start(path: str, args: list[str] | None = None) -> dict[str, Any]:
    global _proc, _active_path, _started_at
    reap()
    if _proc is not None:
        raise PayloadError(f"payload already running: {_active_path}")

    rel_path, target = _safe_payload_path(path)
    LOOT_DIR.mkdir(parents=True, exist_ok=True)
    env = os.environ.copy()
    env["RJ_HEADLESS"] = "1"
    env["RJ_PAYLOAD_MODE"] = "headless"
    env["PYTHONUNBUFFERED"] = "1"
    pythonpath = [str(ROOT_DIR), str(COMPAT_DIR)]
    if env.get("PYTHONPATH"):
        pythonpath.append(env["PYTHONPATH"])
    env["PYTHONPATH"] = os.pathsep.join(pythonpath)

    cmd = ["python3", str(target)]
    if args:
        cmd.extend(str(arg) for arg in args)

    log = PAYLOAD_LOG.open("ab", buffering=0)
    _started_at = time.time()
    _active_path = rel_path
    try:
        _proc = subprocess.Popen(
            cmd,
            cwd=str(ROOT_DIR),
            env=env,
            stdout=log,
            stderr=subprocess.STDOUT,
            start_new_session=True,
            close_fds=True,
        )
    except Exception:
        _active_path = None
        _started_at = None
        log.close()
        raise
    _write_state(True, rel_path, returncode=None)
    return status()


def stop(timeout: float = 8.0) -> dict[str, Any]:
    global _proc
    reap()
    if _proc is None:
        return {"running": False, "path": None, "mode": "headless"}

    proc = _proc
    try:
        os.killpg(proc.pid, signal.SIGINT)
    except Exception:
        try:
            proc.terminate()
        except Exception:
            pass
    deadline = time.monotonic() + timeout
    while proc.poll() is None and time.monotonic() < deadline:
        time.sleep(0.1)
    if proc.poll() is None:
        try:
            os.killpg(proc.pid, signal.SIGTERM)
        except Exception:
            proc.terminate()
    deadline = time.monotonic() + 3.0
    while proc.poll() is None and time.monotonic() < deadline:
        time.sleep(0.1)
    if proc.poll() is None:
        try:
            os.killpg(proc.pid, signal.SIGKILL)
        except Exception:
            proc.kill()
    reap()
    return status()

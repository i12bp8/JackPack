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
_run_id: str | None = None


class PayloadError(RuntimeError):
    pass


def _write_state(running: bool, path: str | None = None, **extra: Any) -> None:
    payload = {
        "running": bool(running),
        "path": path if running else None,
        "pid": _proc.pid if running and _proc else None,
        "mode": "headless",
        "started_at": _started_at if running else None,
        "run_id": _run_id if running else None,
        "log_path": str(PAYLOAD_LOG.relative_to(ROOT_DIR)),
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
    global _proc, _active_path, _started_at, _run_id
    if _proc is None:
        _write_state(False, None)
        return
    rc = _proc.poll()
    if rc is None:
        _write_state(True, _active_path, returncode=None)
        return
    _write_state(False, None, last_path=_active_path, last_run_id=_run_id, returncode=rc, finished_at=time.time())
    _proc = None
    _active_path = None
    _started_at = None
    _run_id = None


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
        "run_id": _run_id,
        "log_path": str(PAYLOAD_LOG.relative_to(ROOT_DIR)),
        "ts": time.time(),
    }


def start(path: str, args: list[str] | None = None, extra_env: dict[str, str] | None = None) -> dict[str, Any]:
    global _proc, _active_path, _started_at, _run_id
    reap()
    if _proc is not None:
        raise PayloadError(f"payload already running: {_active_path}")

    rel_path, target = _safe_payload_path(path)
    LOOT_DIR.mkdir(parents=True, exist_ok=True)
    env = os.environ.copy()
    env["RJ_HEADLESS"] = "1"
    env["RJ_PAYLOAD_MODE"] = "headless"
    env.setdefault("RJ_FRAME_MIRROR", "0")
    env["PYTHONUNBUFFERED"] = "1"
    pythonpath = [str(ROOT_DIR), str(COMPAT_DIR)]
    if env.get("PYTHONPATH"):
        pythonpath.append(env["PYTHONPATH"])
    env["PYTHONPATH"] = os.pathsep.join(pythonpath)
    if extra_env:
        for key, value in extra_env.items():
            if not key or not key.replace("_", "").isalnum():
                continue
            env[str(key)] = str(value)

    cmd = ["python3", str(target)]
    if args:
        cmd.extend(str(arg) for arg in args)

    _started_at = time.time()
    _active_path = rel_path
    _run_id = f"{int(_started_at)}-{os.getpid()}"
    header = (
        f"JackPack payload run {_run_id}\n"
        f"payload: {rel_path}\n"
        f"cwd: {ROOT_DIR}\n"
        f"command: {' '.join(cmd)}\n"
        "\n"
    )
    PAYLOAD_LOG.write_text(header, encoding="utf-8")
    log = PAYLOAD_LOG.open("ab", buffering=0)
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
        _run_id = None
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
        os.killpg(proc.pid, signal.SIGTERM)
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
            os.killpg(proc.pid, signal.SIGINT)
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

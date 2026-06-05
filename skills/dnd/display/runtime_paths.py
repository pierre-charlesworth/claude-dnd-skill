"""runtime_paths.py — resolve the writable runtime-state directory for the
display companion (tokens, queues, device approvals, TLS certs, logs).

These files are deliberately kept OUT of the code directory: a plugin's code
dir is refreshed on `/plugin update` (which would wipe device approvals + certs)
and may be read-only. They live under the data root instead — see
scripts/paths.py `runtime_dir()`. Every display script imports `rt()` from here
so writers and readers always agree on the location.

Process-management files (app.pid, app.log, .cert-server.pid, .scheme) are NOT
runtime state — they are recreated on every launch and stay in the code dir.
"""
import os
import sys
import pathlib

_HERE = os.path.dirname(os.path.abspath(__file__))

# Prefer the canonical resolver in scripts/paths.py; fall back to an identical
# computation if that import fails, so writers/readers never diverge.
sys.path.insert(0, os.path.join(_HERE, os.pardir, "scripts"))
try:
    from paths import runtime_dir as _runtime_dir
    RT = str(_runtime_dir())
except Exception:
    _raw = os.environ.get("DND_RUNTIME_DIR", "").strip()
    if _raw:
        _base = pathlib.Path(_raw).expanduser()
    else:
        _data_root = os.environ.get("DND_CAMPAIGN_ROOT", "").strip() or "~/.claude/dnd"
        _base = pathlib.Path(_data_root).expanduser() / ".runtime"
    try:
        _base.mkdir(parents=True, exist_ok=True)
    except OSError:
        pass
    RT = str(_base)


def rt(name: str) -> str:
    """Absolute path to a runtime-state file by name (e.g. rt('.token'))."""
    return os.path.join(RT, name)

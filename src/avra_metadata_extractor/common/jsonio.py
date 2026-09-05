"""Small JSON helpers: atomic writes and a resumability check."""

import json
import os
import tempfile
from pathlib import Path


def write_json(path, obj, indent=2) -> None:
    """Write ``obj`` as JSON to ``path`` atomically (temp file + rename)."""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp = tempfile.mkstemp(dir=str(path.parent), suffix=".tmp")
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            json.dump(obj, f, indent=indent, ensure_ascii=False)
        os.replace(tmp, path)
    except BaseException:
        try:
            os.unlink(tmp)
        except OSError:
            pass
        raise


def read_json(path):
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def already_done(path, force=False) -> bool:
    """True when ``path`` exists and is non-empty and we are not forcing a redo."""
    if force:
        return False
    p = Path(path)
    return p.exists() and p.stat().st_size > 0

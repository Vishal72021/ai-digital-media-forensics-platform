from __future__ import annotations

from pathlib import Path

__all__ = ["PROJECT_NAME", "CLI_NAME", "DEFAULT_ENCODING", "PROJECT_ROOT", "SCRIPTS_DIRECTORY"]
PROJECT_NAME = "Sentinel AI"
CLI_NAME = "Sentinel AI Developer CLI"
DEFAULT_ENCODING = "utf-8"
PROJECT_ROOT = Path(__file__).resolve().parents[2]
SCRIPTS_DIRECTORY = PROJECT_ROOT / "scripts"

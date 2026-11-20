"""Load the procedure corpus (Markdown files with YAML front matter)."""
from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

import yaml

from car import DATA_DIR


@dataclass(frozen=True)
class Precondition:
    metric: str
    window: str  # "now", "24h" or "7d"
    op: str      # ">=", ">", "<=", "<", "=="
    value: float


@dataclass
class Procedure:
    id: str
    title: str
    topic: str
    specificity: str  # "specific" or "general"
    device_classes: list[str]
    action_severity: str
    preconditions: list[Precondition]
    text: str  # title + body, used for retrieval
    meta: dict = field(default_factory=dict)


def parse_procedure(raw: str) -> Procedure:
    if not raw.startswith("---\n"):
        raise ValueError("procedure file must start with YAML front matter")
    _, fm, body = raw.split("---\n", 2)
    meta = yaml.safe_load(fm)
    pres = [Precondition(p["metric"], str(p["window"]), str(p["op"]), float(p["value"]))
            for p in meta.get("preconditions") or []]
    return Procedure(
        id=meta["id"], title=meta["title"], topic=meta["topic"], specificity=meta["specificity"],
        device_classes=list(meta["device_classes"]), action_severity=meta["action_severity"],
        preconditions=pres, text=body.strip().lstrip("# ").strip(), meta=meta,
    )


def load_corpus(directory: Path | None = None) -> list[Procedure]:
    directory = directory or DATA_DIR / "corpus" / "procedures"
    procs = [parse_procedure(p.read_text(encoding="utf-8")) for p in sorted(directory.glob("*.md"))]
    if not procs:
        raise FileNotFoundError(f"no procedures found in {directory}")
    return procs

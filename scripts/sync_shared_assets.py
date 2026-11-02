#!/usr/bin/env python3
"""Refresh named canonical resources; this explicit maintenance task needs the NH workspace."""

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MAP = ROOT.parent / "neutrinohit-map"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    if not (MAP / "scripts/asset_sync.py").is_file():
        raise SystemExit("The explicit resource sync needs the adjacent neutrinohit-map checkout.")
    for script in ("sync_reveal_assets.py", "sync_book_assets.py"):
        command = [sys.executable, str(MAP / "scripts" / script), "--target", ROOT.name]
        if args.check:
            command.append("--check")
        subprocess.run(command, check=True)
    sys.path.insert(0, str(MAP / "scripts"))
    from asset_sync import Consumer, Copy, build_parser, run
    copies = [Copy(name, "assets/site") for name in (
        "neutrinohit-tokens.css", "neutrinohit-base.css", "neutrinohit-components.css",
        "neutrinohit-projects.css", "neutrinohit-logo.png")]
    copies.append(Copy("../../analytics/cloudflare-web-analytics.html", "shared/html"))
    options = build_parser("Shared site resources", "").parse_args(
        ["--target", ROOT.name] + (["--check"] if args.check else []))
    return run(MAP / "assets/site", [Consumer(ROOT.name, copies)], options,
               "scripts/sync_shared_assets.py")


if __name__ == "__main__":
    raise SystemExit(main())

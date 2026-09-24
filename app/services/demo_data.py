from __future__ import annotations

from shutil import copy2

from app.core.config import Settings


def seed_demo_references(config: Settings) -> int:
    """Copy the bundled, non-private lecturer corpus into an empty hosted data folder."""

    source_dir = config.demo_corpus_dir
    if not source_dir.is_dir():
        return 0

    config.reference_dir.mkdir(parents=True, exist_ok=True)
    copied = 0
    for source in sorted(source_dir.iterdir()):
        if not source.is_file() or source.suffix.lower() not in config.allowed_extensions:
            continue
        destination = config.reference_dir / source.name
        if destination.exists():
            continue
        try:
            copy2(source, destination)
        except OSError:
            # Seeding is a convenience for the hosted demo and must not prevent
            # startup if a local data directory has inherited restrictive ACLs.
            continue
        copied += 1
    return copied

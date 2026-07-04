"""
auto-sorter — раскладывает файлы в папке по категориям (по расширению) и по дате.

Использование:
    python sorter.py ~/Downloads
    python sorter.py ~/Downloads --by date
    python sorter.py ~/Downloads --dry-run

Никаких внешних зависимостей — только стандартная библиотека.
"""

from __future__ import annotations

import argparse
import shutil
import sys
from datetime import datetime
from pathlib import Path

EXTENSION_MAP: dict[str, str] = {
    ".jpg": "images", ".jpeg": "images", ".png": "images", ".gif": "images",
    ".webp": "images", ".svg": "images", ".heic": "images",
    ".mp4": "video", ".mov": "video", ".mkv": "video", ".avi": "video",
    ".mp3": "audio", ".wav": "audio", ".flac": "audio", ".m4a": "audio",
    ".pdf": "documents", ".doc": "documents", ".docx": "documents",
    ".xls": "documents", ".xlsx": "documents", ".ppt": "documents",
    ".pptx": "documents", ".txt": "documents", ".odt": "documents",
    ".zip": "archives", ".rar": "archives", ".7z": "archives", ".tar": "archives",
    ".gz": "archives",
    ".py": "code", ".js": "code", ".ts": "code", ".java": "code",
    ".cpp": "code", ".c": "code", ".go": "code", ".rs": "code", ".sh": "code",
    ".exe": "installers", ".msi": "installers", ".dmg": "installers",
    ".apk": "installers", ".deb": "installers",
}

DEFAULT_CATEGORY = "other"


def category_for(path: Path) -> str:
    return EXTENSION_MAP.get(path.suffix.lower(), DEFAULT_CATEGORY)


def date_bucket_for(path: Path) -> str:
    ts = path.stat().st_mtime
    return datetime.fromtimestamp(ts).strftime("%Y-%m")


def plan_moves(folder: Path, mode: str) -> list[tuple[Path, Path]]:
    moves: list[tuple[Path, Path]] = []
    for entry in folder.iterdir():
        if entry.is_dir():
            continue
        if entry.name.startswith("."):
            continue

        bucket = date_bucket_for(entry) if mode == "date" else category_for(entry)
        destination_dir = folder / bucket
        destination = destination_dir / entry.name

        # avoid collisions
        counter = 1
        while destination.exists():
            destination = destination_dir / f"{entry.stem}_{counter}{entry.suffix}"
            counter += 1

        moves.append((entry, destination))
    return moves


def apply_moves(moves: list[tuple[Path, Path]], dry_run: bool) -> None:
    for source, destination in moves:
        rel_dest = destination.relative_to(destination.parents[len(destination.parts) - 2]) if False else destination
        print(f"{source.name}  ->  {destination.parent.name}/{destination.name}")
        if not dry_run:
            destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.move(str(source), str(destination))


def main() -> int:
    parser = argparse.ArgumentParser(description="Раскладывает файлы в папке по подкаталогам.")
    parser.add_argument("folder", type=str, help="Папка, которую нужно отсортировать")
    parser.add_argument(
        "--by", choices=["type", "date"], default="type",
        help="Критерий сортировки: type (по типу файла) или date (по месяцу изменения)",
    )
    parser.add_argument("--dry-run", action="store_true", help="Показать план без реального перемещения файлов")
    args = parser.parse_args()

    folder = Path(args.folder).expanduser().resolve()
    if not folder.is_dir():
        print(f"Ошибка: {folder} — не папка или не существует", file=sys.stderr)
        return 1

    moves = plan_moves(folder, mode=args.by)
    if not moves:
        print("Нечего сортировать — папка уже пуста или содержит только вложенные папки.")
        return 0

    apply_moves(moves, dry_run=args.dry_run)

    if args.dry_run:
        print(f"\nDry run: показано {len(moves)} перемещений, файлы не тронуты.")
    else:
        print(f"\nГотово: перемещено {len(moves)} файлов.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

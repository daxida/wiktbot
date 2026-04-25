import argparse
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

from main import repl_ja_template
from wago import repl_wago
from trans import repl_trans


@dataclass
class Args:
    ipath: Path
    opath: Path
    command: str | None
    fixture_dir: Path | None = None


def repl(s: str) -> str:
    s = repl_ja_template(s)
    s = repl_wago(s)
    s = repl_trans(s)
    return s


def cmd_run(args: Args) -> None:
    text = args.ipath.read_text(encoding="utf-8")
    # Overwrite with stripped contents for simpler diffs
    args.ipath.write_text(text.strip(), encoding="utf-8")

    result = repl(text)
    args.opath.write_text(result, encoding="utf-8")
    print(f"Wrote output to {args.opath}")


def cmd_snapshot(args: Args) -> None:
    assert args.fixture_dir is not None
    args.fixture_dir.mkdir(parents=True, exist_ok=True)
    now = datetime.now().strftime("%Y-%m-%d")

    input_text = args.ipath.read_text(encoding="utf-8") if args.ipath.exists() else ""
    output_text = args.opath.read_text(encoding="utf-8") if args.opath.exists() else ""

    dest = args.fixture_dir / f"test_{now}.txt"
    dest.write_text(f"{input_text}\n</>\n{output_text}", encoding="utf-8")
    print(f"Snapshot written to {dest}")


def parse_args() -> Args:
    parser = argparse.ArgumentParser(description="repl_ja_template CLI")
    parser.add_argument(
        "--input", default="input.txt", help="Input file (default: input.txt)"
    )
    parser.add_argument(
        "--output", default="output.txt", help="Output file (default: output.txt)"
    )

    subparsers = parser.add_subparsers(dest="command")
    subparsers.add_parser("run", help="Process input.txt and write output.txt")
    snap = subparsers.add_parser(
        "snapshot", help="Copy input/output to a fixture folder"
    )
    snap.add_argument(
        "fixture_dir",
        nargs="?",
        default="fixtures",
        help="Destination folder (default: fixtures)",
    )
    args = parser.parse_args()

    fixture_dir = None
    if _fixture_dir := getattr(args, "fixture_dir", None):
        fixture_dir = Path(_fixture_dir)

    return Args(
        ipath=Path(args.input),
        opath=Path(args.output),
        command=args.command,
        fixture_dir=fixture_dir,
    )


def main() -> None:
    args = parse_args()

    match args.command:
        case "snapshot":
            cmd_snapshot(args)
        case _:
            cmd_run(args)


if __name__ == "__main__":
    main()

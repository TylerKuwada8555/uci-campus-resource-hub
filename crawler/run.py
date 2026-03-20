from __future__ import annotations

import argparse
import logging
from pathlib import Path
import sys


ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Crawl UCI websites for student resources.")
    parser.add_argument(
        "--output",
        type=Path,
        default=None,
        help="Optional output path for the generated JSON file.",
    )
    parser.add_argument(
        "--max-pages",
        type=int,
        default=None,
        help="Maximum number of pages to visit in this run.",
    )
    parser.add_argument(
        "--max-depth",
        type=int,
        default=None,
        help="Maximum discovery depth from the seed URLs.",
    )
    parser.add_argument(
        "--seed-file",
        type=Path,
        default=None,
        help="Optional newline-delimited seed URL file.",
    )
    parser.add_argument(
        "--log-level",
        default="INFO",
        choices=("DEBUG", "INFO", "WARNING", "ERROR"),
        help="Logging verbosity for the crawl.",
    )
    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()

    logging.basicConfig(level=getattr(logging, args.log_level), format="%(levelname)s: %(message)s")

    try:
        from crawler.config import CrawlConfig
        from crawler.pipeline import run_crawl, save_records
    except ModuleNotFoundError as exc:
        missing = exc.name or "dependency"
        parser.exit(
            1,
            f"Missing Python dependency: {missing}. Run `python3 -m pip install -r requirements.txt` and try again.\n",
        )

    config = CrawlConfig()
    if args.output is not None:
        config.output_path = args.output
    if args.max_pages is not None:
        config.max_pages = args.max_pages
    if args.max_depth is not None:
        config.max_depth = args.max_depth

    records = run_crawl(config, seed_file=args.seed_file)
    saved_path = save_records(records, config.output_path)
    print(f"Saved {len(records)} resources to {saved_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

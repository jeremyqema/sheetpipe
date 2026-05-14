"""Command-line interface for sheetpipe."""

import argparse
import sys
from typing import Optional

from sheetpipe.pipeline import PipelineConfig, run_pipeline


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="sheetpipe",
        description="Sync Google Sheets data into PostgreSQL.",
    )
    parser.add_argument("spreadsheet_id", help="Google Sheets spreadsheet ID")
    parser.add_argument("sheet_range", help="Sheet range, e.g. Sheet1!A1:Z")
    parser.add_argument("dsn", help="PostgreSQL connection string")
    parser.add_argument(
        "--table",
        default=None,
        help="Target table name (defaults to sanitized sheet name)",
    )
    parser.add_argument(
        "--drop",
        action="store_true",
        default=False,
        help="Drop and recreate the table before loading",
    )
    parser.add_argument(
        "--keep-invalid",
        action="store_true",
        default=False,
        help="Keep invalid rows instead of dropping them",
    )
    parser.add_argument(
        "--report-format",
        choices=["text", "json"],
        default="text",
        help="Validation report output format (default: text)",
    )
    parser.add_argument(
        "--credentials",
        default=None,
        help="Path to Google service account credentials JSON file",
    )
    return parser


def main(argv: Optional[list] = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    config = PipelineConfig(
        spreadsheet_id=args.spreadsheet_id,
        sheet_range=args.sheet_range,
        dsn=args.dsn,
        table_name=args.table,
        drop_if_exists=args.drop,
        drop_invalid_rows=not args.keep_invalid,
        report_format=args.report_format,
        credentials_path=args.credentials,
    )

    try:
        result = run_pipeline(config)
        print(result["report"])
        print(f"Rows loaded: {result['rows_loaded']}")
        return 0
    except Exception as exc:  # pylint: disable=broad-except
        print(f"Error: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())

"""Main orchestrator for Guanyuan data fetching

This module provides the main execution logic that coordinates all other modules.
It's designed to be called from Claude Code SKILL.md execution context.

Supports both the original hardcoded mode (backward compatible) and
config-file-driven mode for arbitrary dashboards.
"""

import sys
import argparse
from pathlib import Path
from typing import Dict, Any, List, Optional
import json

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from scripts.guanyuan_fetch.card_config import (
    CARDS,
    PAGE_ID,
    PAGE_NAME,
    START_DATE,
    CardConfig,
    DashboardConfig,
    get_end_date,
    load_config,
    generate_output_filename,
)
from scripts.guanyuan_fetch.filter_builder import build_filters, validate_filters
from scripts.guanyuan_fetch.data_processor import process_and_save, ProcessingError
from scripts.guanyuan_fetch.metadata_writer import generate_metadata, write_metadata
from scripts.guanyuan_fetch.excel_writer import write_cards_to_excel, ExcelWriterError


def parse_args(args: List[str] = None) -> argparse.Namespace:
    """Parse command-line arguments.

    Args:
        args: Argument list (default: sys.argv[1:])

    Returns:
        Parsed namespace with all parameters
    """
    parser = argparse.ArgumentParser(
        description="Guanyuan Data Fetcher - fetch data from Guanyuan dashboards"
    )
    parser.add_argument(
        "--config",
        type=str,
        default=None,
        help="Path to JSON config file (default: use built-in config for '1.2 核心指标')",
    )
    parser.add_argument(
        "--start-date",
        type=str,
        default=None,
        help="Start date in YYYY-MM-DD format (default: from config or 2025-12-01)",
    )
    parser.add_argument(
        "--end-date",
        type=str,
        default=None,
        help="End date in YYYY-MM-DD format (default: today)",
    )
    parser.add_argument(
        "--format",
        choices=["csv", "excel"],
        default="excel",
        help="Output format: csv or excel (default: excel)",
    )
    parser.add_argument(
        "--output-dir",
        type=str,
        default="Data/guanyuan",
        help="Output directory (default: Data/guanyuan)",
    )
    parser.add_argument(
        "--page-id",
        type=str,
        default=None,
        help="Override page ID from config",
    )
    # Keep backward compatibility with --excel flag
    parser.add_argument(
        "--excel",
        action="store_true",
        help="Shorthand for --format=excel (backward compatible)",
    )

    parsed = parser.parse_args(args)

    # Handle --excel shorthand
    if parsed.excel:
        parsed.format = "excel"

    return parsed


def build_runtime_config(
    config_path: Optional[str] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    page_id: Optional[str] = None,
) -> DashboardConfig:
    """Build runtime configuration by loading config file and applying overrides.

    Args:
        config_path: Path to JSON config file (None = use defaults)
        start_date: Override start date
        end_date: Override end date
        page_id: Override page ID

    Returns:
        DashboardConfig with all overrides applied
    """
    dashboard = load_config(config_path)

    # Apply CLI overrides
    if start_date is not None:
        dashboard.start_date = start_date
    if end_date is not None:
        dashboard.end_date = end_date if end_date != "today" else None
    if page_id is not None:
        dashboard.page_id = page_id

    return dashboard


def prepare_fetch_params(card_config: CardConfig, dashboard: DashboardConfig = None) -> Dict[str, Any]:
    """Prepare parameters for MCP get_card_data call

    Args:
        card_config: CardConfig object
        dashboard: DashboardConfig for date range (None = use module defaults)

    Returns:
        Dictionary with cardId and cardFilters ready for MCP call
    """
    if dashboard is not None:
        start_date = dashboard.start_date
        end_date = dashboard.get_end_date()
    else:
        start_date = START_DATE
        end_date = get_end_date()

    # Build filters
    filters = build_filters(card_config.filter_template, start_date, end_date)

    # Validate filters
    validate_filters(filters)

    return {
        "cardId": card_config.card_id,
        "cardFilters": filters,
        "card_name": card_config.card_name,
        "output_filename": card_config.output_filename,
        "start_date": start_date,
        "end_date": end_date,
    }


def process_card_response(
    mcp_response: Dict[str, Any],
    card_config: CardConfig,
    output_dir: Path = Path("Data/guanyuan"),
) -> Dict[str, Any]:
    """Process MCP response and save to CSV

    Args:
        mcp_response: Response from MCP get_card_data call
        card_config: CardConfig object
        output_dir: Output directory

    Returns:
        Processing result dictionary
    """
    result = process_and_save(
        mcp_response,
        card_config.output_filename,
        output_dir,
    )

    # Add card info
    result["card_id"] = card_config.card_id
    result["card_name"] = card_config.card_name

    return result


def create_initial_metadata(dashboard: DashboardConfig = None) -> Dict[str, Any]:
    """Create initial metadata structure

    Args:
        dashboard: DashboardConfig (None = use module defaults)

    Returns:
        Empty metadata dictionary
    """
    if dashboard is not None:
        page_id = dashboard.page_id
        page_name = dashboard.page_name
        start_date = dashboard.start_date
        end_date = dashboard.get_end_date()
        total_count = len(dashboard.cards)
    else:
        page_id = PAGE_ID
        page_name = PAGE_NAME
        start_date = START_DATE
        end_date = get_end_date()
        total_count = len(CARDS)

    return {
        "fetch_timestamp": None,  # Will be set when writing
        "source": {
            "page_id": page_id,
            "page_name": page_name,
            "page_url": f"http://guandata.dmz.prod.caijj.net/page/{page_id}",
        },
        "query_parameters": {
            "date_dimension": "月",
            "start_date": start_date,
            "end_date": end_date,
            "filters_note": "不用其他筛选 (no additional filters)",
        },
        "cards_fetched": {
            "total_count": total_count,
            "success_count": 0,
            "failed_count": 0,
        },
        "data_summary": [],
        "errors": [],
    }


def get_all_cards(dashboard: DashboardConfig = None) -> List[CardConfig]:
    """Get all card configurations

    Args:
        dashboard: DashboardConfig (None = use module defaults)

    Returns:
        List of CardConfig objects
    """
    if dashboard is not None:
        return dashboard.cards
    return CARDS


def prepare_all_fetch_params(dashboard: DashboardConfig = None) -> List[Dict[str, Any]]:
    """Prepare fetch parameters for all cards

    Args:
        dashboard: DashboardConfig (None = use module defaults)

    Returns:
        List of parameter dictionaries for all cards
    """
    cards = get_all_cards(dashboard)
    return [prepare_fetch_params(card, dashboard) for card in cards]


def fetch_all_cards_to_excel(
    mcp_responses: List[Dict[str, Any]],
    output_filename: str = None,
    output_dir: Path = Path("Data/guanyuan"),
    dashboard: DashboardConfig = None,
) -> Dict[str, Any]:
    """Coordinate Excel output for all cards

    Args:
        mcp_responses: List of MCP responses, each should be a dict with:
            - card_name: Name of the card
            - response_data: MCP get_card_data response
        output_filename: Name of output Excel file (default: auto-generated)
        output_dir: Output directory
        dashboard: DashboardConfig for metadata (None = use module defaults)

    Returns:
        Dictionary with excel_result, metadata, metadata_path

    Raises:
        ExcelWriterError: If Excel writing fails
    """
    # Generate default filename if not provided
    if output_filename is None:
        if dashboard is not None:
            end_date = dashboard.get_end_date()
            output_filename = generate_output_filename(
                dashboard.page_name, dashboard.start_date, end_date
            )
        else:
            end_date = get_end_date()
            date_str = end_date.replace("-", "")
            output_filename = f"guanyuan_monthly_{date_str}.xlsx"

    # Write all cards to Excel
    excel_result = write_cards_to_excel(
        mcp_responses,
        output_filename,
        output_dir
    )

    # Generate metadata
    metadata = create_initial_metadata(dashboard)
    metadata["output_format"] = "excel"
    metadata["output_file"] = excel_result["output_path"]

    # Update metadata with results
    for sheet_info in excel_result.get("sheets", []):
        if sheet_info.get("status") == "success":
            metadata["cards_fetched"]["success_count"] += 1
            metadata["data_summary"].append({
                "card_name": sheet_info.get("original_name"),
                "sheet_name": sheet_info.get("sheet_name"),
                "row_count": sheet_info.get("row_count"),
                "column_count": sheet_info.get("column_count"),
                "columns": sheet_info.get("columns")
            })
        else:
            metadata["cards_fetched"]["failed_count"] += 1
            if sheet_info.get("error"):
                metadata["errors"].append({
                    "card_name": sheet_info.get("sheet_name"),
                    "error": sheet_info.get("error")
                })

    # Write metadata
    metadata_path = write_metadata(metadata, output_dir)

    return {
        "excel_result": excel_result,
        "metadata": metadata,
        "metadata_path": metadata_path
    }


def main():
    """Main CLI entry point"""
    args = parse_args()

    # Build runtime config
    dashboard = build_runtime_config(
        config_path=args.config,
        start_date=args.start_date,
        end_date=args.end_date,
        page_id=args.page_id,
    )
    output_dir = Path(args.output_dir)

    print("Guanyuan Data Fetcher")
    print(f"  Page: {dashboard.page_name} ({dashboard.page_id})")
    print(f"  Time range: {dashboard.start_date} to {dashboard.get_end_date()}")
    print(f"  Cards: {len(dashboard.cards)}")
    print(f"  Format: {args.format}")
    print(f"  Output dir: {output_dir}")
    if args.config:
        print(f"  Config: {args.config}")

    if args.format == "excel":
        print("\nExcel mode: Prepare parameters for all cards")
        all_params = prepare_all_fetch_params(dashboard)
        print(f"Prepared {len(all_params)} card parameters")
        print("\nNote: Excel output requires MCP responses.")
        print("Call fetch_all_cards_to_excel() with MCP responses to generate Excel file.")
    else:
        print("\nCSV mode: Display card information")
        for i, card in enumerate(dashboard.cards, 1):
            print(f"\n{i}. {card.card_name}")
            print(f"   Card ID: {card.card_id}")
            print(f"   Template: {card.filter_template}")
            print(f"   Output: {card.output_filename}")

            # Prepare fetch parameters
            params = prepare_fetch_params(card, dashboard)
            print(f"   Filters: {len(params['cardFilters'])} filters")


if __name__ == "__main__":
    main()

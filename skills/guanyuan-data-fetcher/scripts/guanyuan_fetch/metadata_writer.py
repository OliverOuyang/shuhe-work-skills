"""Metadata Writer Module

Generates _metadata.json file with execution information and data summaries.
"""

import json
from typing import Dict, List, Any
from datetime import datetime
from pathlib import Path


def generate_metadata(
    page_id: str,
    page_name: str,
    cards_processed: List[Dict[str, Any]],
    start_date: str,
    end_date: str,
    errors: List[Dict[str, str]] = None,
) -> Dict[str, Any]:
    """Generate metadata dictionary

    Args:
        page_id: Guanyuan page ID
        page_name: Guanyuan page name
        cards_processed: List of card processing results, each containing:
            - card_id: str
            - card_name: str
            - output_path: str
            - row_count: int
            - column_count: int
            - headers: List[str]
        start_date: Query start date
        end_date: Query end date
        errors: Optional list of error dictionaries with 'card_id', 'card_name', 'error' keys

    Returns:
        Metadata dictionary ready for JSON serialization
    """
    metadata = {
        "fetch_timestamp": datetime.now().isoformat(),
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
            "total_count": len(cards_processed),
            "success_count": len(cards_processed),
            "failed_count": len(errors) if errors else 0,
        },
        "data_summary": [],
        "errors": errors or [],
    }

    # Add data summary for each card
    for card in cards_processed:
        summary = {
            "card_id": card["card_id"],
            "card_name": card["card_name"],
            "output_file": card["output_path"],
            "row_count": card["row_count"],
            "column_count": card["column_count"],
            "columns": card["headers"],
        }
        metadata["data_summary"].append(summary)

    return metadata


def write_metadata(
    metadata: Dict[str, Any],
    output_dir: Path = Path("Data/guanyuan"),
    filename: str = "_metadata.json",
) -> Path:
    """Write metadata to JSON file

    Args:
        metadata: Metadata dictionary
        output_dir: Directory to save metadata file
        filename: Metadata filename (default: _metadata.json)

    Returns:
        Path to written metadata file

    Raises:
        IOError: If file write fails
    """
    output_dir.mkdir(parents=True, exist_ok=True)
    output_path = output_dir / filename

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(metadata, f, ensure_ascii=False, indent=2)

    return output_path


def add_card_result(
    metadata: Dict[str, Any],
    card_id: str,
    card_name: str,
    output_path: str,
    row_count: int,
    column_count: int,
    headers: List[str],
) -> None:
    """Add a card processing result to metadata (in-place modification)

    Args:
        metadata: Metadata dictionary to update
        card_id: Card ID
        card_name: Card name
        output_path: Path to output CSV
        row_count: Number of rows
        column_count: Number of columns
        headers: Column names
    """
    summary = {
        "card_id": card_id,
        "card_name": card_name,
        "output_file": output_path,
        "row_count": row_count,
        "column_count": column_count,
        "columns": headers,
    }
    metadata["data_summary"].append(summary)
    metadata["cards_fetched"]["success_count"] = len(metadata["data_summary"])


def add_error(
    metadata: Dict[str, Any],
    card_id: str,
    card_name: str,
    error_message: str,
) -> None:
    """Add an error to metadata (in-place modification)

    Args:
        metadata: Metadata dictionary to update
        card_id: Card ID that failed
        card_name: Card name that failed
        error_message: Error description
    """
    error = {
        "card_id": card_id,
        "card_name": card_name,
        "error": error_message,
    }
    metadata["errors"].append(error)
    metadata["cards_fetched"]["failed_count"] = len(metadata["errors"])

"""Excel Writer Module

Processes MCP API responses and writes all cards to a single Excel file with multiple sheets.
"""

import pandas as pd
from typing import Dict, List, Any
from pathlib import Path
from datetime import datetime


class ExcelWriterError(Exception):
    """Exception raised during Excel writing"""
    pass


def parse_card_to_dataframe(response_data: Dict, card_name: str) -> pd.DataFrame:
    """Parse MCP get_card_data response into pandas DataFrame

    Args:
        response_data: MCP response dictionary with 'data' field
        card_name: Name of the card for error messages

    Returns:
        pandas DataFrame with card data

    Raises:
        ExcelWriterError: If response structure is invalid
    """
    try:
        # Handle nested response structure: response.data.data
        if "data" in response_data and "data" in response_data["data"]:
            data = response_data["data"]["data"]
        else:
            data = response_data.get("data", {})

        # Extract headers
        headers_obj = data.get("headers", [])
        if not headers_obj:
            raise ExcelWriterError(f"Card '{card_name}': Response missing 'headers'")

        # Headers can be list of strings or list of dicts with 'name' key
        if isinstance(headers_obj[0], dict):
            headers = [h.get("name", f"column_{i}") for i, h in enumerate(headers_obj)]
        else:
            headers = headers_obj

        # Extract values
        values = data.get("values", [])
        if not isinstance(values, list):
            raise ExcelWriterError(f"Card '{card_name}': 'values' must be a list")

        if not values:
            raise ExcelWriterError(f"Card '{card_name}': No data rows returned")

        # Create DataFrame
        df = pd.DataFrame(values, columns=headers)
        return df

    except (KeyError, IndexError, AttributeError) as e:
        raise ExcelWriterError(f"Card '{card_name}': Invalid response structure - {e}")


def write_cards_to_excel(
    cards_data: List[Dict[str, Any]],
    output_filename: str,
    output_dir: Path = Path("Data/guanyuan"),
) -> Dict[str, Any]:
    """Write multiple card responses to a single Excel file with multiple sheets

    Args:
        cards_data: List of dictionaries, each containing:
            - card_name: Name of the card (used as sheet name)
            - response_data: MCP response for this card
        output_filename: Name of output Excel file (should end with .xlsx)
        output_dir: Directory to save Excel file

    Returns:
        Dictionary with processing summary:
        {
            "output_path": str,
            "sheets": List[Dict] with sheet details
        }

    Raises:
        ExcelWriterError: If writing fails
    """
    if not output_filename.endswith('.xlsx'):
        output_filename += '.xlsx'

    output_path = output_dir / output_filename
    output_dir.mkdir(parents=True, exist_ok=True)

    sheets_summary = []

    try:
        with pd.ExcelWriter(output_path, engine='openpyxl') as writer:
            for card_data in cards_data:
                card_name = card_data.get("card_name", "Unknown")
                response_data = card_data.get("response_data")

                if not response_data:
                    sheets_summary.append({
                        "sheet_name": card_name,
                        "status": "skipped",
                        "reason": "No response data"
                    })
                    continue

                try:
                    # Parse to DataFrame
                    df = parse_card_to_dataframe(response_data, card_name)

                    # Sanitize sheet name (Excel has 31 char limit and forbidden chars)
                    sheet_name = card_name[:31]
                    for char in ['\\', '/', '?', '*', '[', ']', ':']:
                        sheet_name = sheet_name.replace(char, '_')

                    # Write to Excel sheet
                    df.to_excel(writer, sheet_name=sheet_name, index=False)

                    sheets_summary.append({
                        "sheet_name": sheet_name,
                        "original_name": card_name,
                        "status": "success",
                        "row_count": len(df),
                        "column_count": len(df.columns),
                        "columns": list(df.columns)
                    })

                except ExcelWriterError as e:
                    sheets_summary.append({
                        "sheet_name": card_name,
                        "status": "error",
                        "error": str(e)
                    })

        # Check if at least one sheet was written successfully
        success_count = sum(1 for s in sheets_summary if s.get("status") == "success")
        if success_count == 0:
            raise ExcelWriterError("No sheets were written successfully")

        return {
            "output_path": str(output_path),
            "total_sheets": len(sheets_summary),
            "success_sheets": success_count,
            "sheets": sheets_summary
        }

    except Exception as e:
        raise ExcelWriterError(f"Failed to write Excel file: {e}")


def validate_excel_output(excel_path: Path) -> bool:
    """Validate that an Excel file was created successfully

    Args:
        excel_path: Path to Excel file

    Returns:
        True if file exists and is readable

    Raises:
        ExcelWriterError: If validation fails
    """
    if not excel_path.exists():
        raise ExcelWriterError(f"Excel file not found: {excel_path}")

    # Try to read file to verify it's valid Excel
    try:
        with pd.ExcelFile(excel_path) as xl:
            if len(xl.sheet_names) == 0:
                raise ExcelWriterError(f"Excel file has no sheets: {excel_path}")
    except Exception as e:
        raise ExcelWriterError(f"Cannot read Excel file: {e}")

    return True

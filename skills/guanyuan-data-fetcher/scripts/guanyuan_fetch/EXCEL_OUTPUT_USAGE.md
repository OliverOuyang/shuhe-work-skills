# Excel Output Usage Guide

## Overview

The `guanyuan_fetch` module now supports outputting all 5 cards to a single Excel file with multiple sheets.

## Functions

### `prepare_all_fetch_params()`

Prepares fetch parameters for all 5 cards.

**Returns:**
- List of parameter dictionaries for MCP calls

**Example:**
```python
from scripts.guanyuan_fetch.main import prepare_all_fetch_params

params = prepare_all_fetch_params()
# params is a list of 5 dictionaries, each containing:
# - cardId
# - cardFilters
# - card_name
# - output_filename
# - start_date
# - end_date
```

### `fetch_all_cards_to_excel(mcp_responses, output_filename=None, output_dir=Path("Data/guanyuan"))`

Writes all card responses to a single Excel file with multiple sheets.

**Args:**
- `mcp_responses`: List of MCP responses, each containing:
  - `card_name`: Name of the card
  - `response_data`: MCP `get_card_data` response
- `output_filename`: Optional output filename (default: `guanyuan_monthly_YYYYMMDD.xlsx`)
- `output_dir`: Output directory (default: `Data/guanyuan`)

**Returns:**
Dictionary with:
- `excel_result`: Excel writing result with sheet details
- `metadata`: Metadata dictionary with summary
- `metadata_path`: Path to metadata file

**Example:**
```python
from scripts.guanyuan_fetch.main import fetch_all_cards_to_excel

# After collecting all MCP responses
mcp_responses = [
    {
        "card_name": "首次放款客户_流失运营_by 6类人群",
        "response_data": {...}  # MCP response
    },
    {
        "card_name": "首次放款客户次月留存",
        "response_data": {...}  # MCP response
    },
    # ... 3 more cards
]

result = fetch_all_cards_to_excel(mcp_responses)
print(f"Excel file: {result['excel_result']['output_path']}")
print(f"Success sheets: {result['excel_result']['success_sheets']}")
```

## Command Line Usage

### CSV Mode (Default - Backward Compatible)
```bash
python scripts/guanyuan_fetch/main.py
# or
python scripts/guanyuan_fetch/main.py --format csv
```

### Excel Mode
```bash
python scripts/guanyuan_fetch/main.py --format excel
```

## Workflow

1. **Prepare parameters:**
   ```python
   from scripts.guanyuan_fetch.main import prepare_all_fetch_params
   params = prepare_all_fetch_params()
   ```

2. **Call MCP for each card:**
   Use the params to call MCP `get_card_data` tool and collect responses.

3. **Generate Excel:**
   ```python
   from scripts.guanyuan_fetch.main import fetch_all_cards_to_excel
   result = fetch_all_cards_to_excel(mcp_responses)
   ```

## Output Structure

### Excel File
- **Filename:** `guanyuan_monthly_YYYYMMDD.xlsx`
- **Location:** `Data/guanyuan/`
- **Sheets:** One sheet per card (up to 5 sheets)
- **Sheet names:** Sanitized card names (max 31 chars, no forbidden chars)

### Metadata File
- **Filename:** `_metadata.json`
- **Location:** Same as Excel file
- **Content:**
  - Fetch timestamp
  - Source information
  - Query parameters
  - Success/failure counts
  - Sheet-level summaries (row counts, columns)
  - Error details (if any)

## Error Handling

- If a card fails to parse, it's skipped but other cards continue
- Metadata tracks success/failure for each card
- At least one successful card is required to generate the Excel file

## Backward Compatibility

The existing CSV output functionality remains unchanged:
- `process_card_response()` still saves individual CSV files
- All existing scripts using CSV output continue to work

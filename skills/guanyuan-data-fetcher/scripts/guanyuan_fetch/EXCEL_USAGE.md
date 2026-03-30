# Excel Multi-Sheet Output Usage

## Overview

The `data_processor.py` module now supports writing multiple card data to a single Excel file with separate sheets.

## New Functions

### `write_excel_multi_sheet()`

Writes multiple cards to an Excel file with separate sheets.

```python
from pathlib import Path
from data_processor import write_excel_multi_sheet

cards_data = [
    {
        "sheet_name": "卡片1",
        "headers": ["列A", "列B", "列C"],
        "rows": [
            ["数据1", "数据2", "数据3"],
            ["数据4", "数据5", "数据6"],
        ],
    },
    {
        "sheet_name": "卡片2",
        "headers": ["ID", "名称", "金额"],
        "rows": [
            [1, "项目A", 1000.5],
            [2, "项目B", 2000.75],
        ],
    },
]

output_path = Path("output.xlsx")
write_excel_multi_sheet(output_path, cards_data)
```

### `process_and_save_excel()`

Processes multiple MCP card responses and saves to a single Excel file.

```python
from pathlib import Path
from data_processor import process_and_save_excel
from card_config import CARDS

# Assume you have fetched responses for multiple cards
cards_responses = [...]  # List of MCP get_card_data responses
cards_config = CARDS[:3]  # First 3 cards

result = process_and_save_excel(
    cards_responses=cards_responses,
    cards_config=cards_config,
    output_filename="guanyuan_data.xlsx",
    output_dir=Path("Data/guanyuan"),
)

print(f"Created: {result['output_path']}")
print(f"Total rows: {result['total_rows']}")
print(f"Sheet count: {result['sheet_count']}")
```

## Features

- **UTF-8 Support**: Full Chinese character support
- **Sheet Name Truncation**: Automatically truncates sheet names to 31 characters (Excel limit)
- **Auto File Extension**: Automatically adds `.xlsx` if missing
- **Empty Card Handling**: Allows empty cards (0 rows)
- **Error Context**: Clear error messages with card context

## Return Format

`process_and_save_excel()` returns a summary dictionary:

```python
{
    "output_path": str,           # Full path to output file
    "total_rows": int,            # Total rows across all sheets
    "sheet_count": int,           # Number of sheets created
    "sheets": [                   # Per-sheet statistics
        {
            "sheet_name": str,    # Sheet name (truncated to 31 chars)
            "row_count": int,     # Number of data rows
            "column_count": int,  # Number of columns
        },
        ...
    ]
}
```

## Requirements

Install openpyxl:

```bash
pip install openpyxl
```

## Migration from CSV

The existing `write_csv_utf8_bom()` and `process_and_save()` functions remain unchanged for backward compatibility.

**CSV workflow (unchanged):**
```python
from data_processor import process_and_save

result = process_and_save(
    response_data=response,
    output_filename="data.csv",
)
```

**Excel workflow (new):**
```python
from data_processor import process_and_save_excel

result = process_and_save_excel(
    cards_responses=[response1, response2, response3],
    cards_config=[config1, config2, config3],
    output_filename="data.xlsx",
)
```

## Notes

- Excel sheet names are limited to 31 characters and will be automatically truncated
- The module gracefully handles the case when openpyxl is not installed (raises ProcessingError with installation instructions)
- Column widths are set to a default of 15 for readability

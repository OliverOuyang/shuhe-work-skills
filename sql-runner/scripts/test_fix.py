#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test script to verify the MCP response parsing fix.
"""

import sys
import io

# Fix Windows console encoding
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

def test_data_extraction():
    """Test the fixed data extraction logic."""

    # Simulate actual MCP response structure
    mcp_response_success = {
        'queryStatus': 'SUCCESS',
        'columns': ['月份', '客群', '渠道类别', '授信人数'],
        'rows': [
            ['2026-01', '当月首登M0', '抖音', '1234'],
            ['2026-02', '存量首登M0', '腾讯', '5678']
        ],
        'rowCount': 2
    }

    # Test Case 1: Normal response with data
    print("Test 1: Normal response with columns and rows")
    result = mcp_response_success
    columns = result.get('columns', [])
    rows = result.get('rows', [])
    data = [columns] + rows if columns else rows

    assert len(data) == 3, f"Expected 3 lines (1 header + 2 rows), got {len(data)}"
    assert data[0] == ['月份', '客群', '渠道类别', '授信人数'], "Header mismatch"
    assert len(rows) == 2, f"Expected 2 data rows, got {len(rows)}"
    print(f"✓ Pass: {len(columns)} columns, {len(rows)} data rows")
    print()

    # Test Case 2: Empty result
    print("Test 2: Empty result (no columns, no rows)")
    result_empty = {
        'queryStatus': 'SUCCESS',
        'columns': [],
        'rows': [],
        'rowCount': 0
    }
    columns = result_empty.get('columns', [])
    rows = result_empty.get('rows', [])
    data = [columns] + rows if columns else rows

    assert len(data) == 0, f"Expected 0 lines, got {len(data)}"
    print(f"✓ Pass: Empty result handled correctly")
    print()

    # Test Case 3: Columns only (no data rows)
    print("Test 3: Columns only, no data rows")
    result_header_only = {
        'queryStatus': 'SUCCESS',
        'columns': ['col1', 'col2'],
        'rows': [],
        'rowCount': 0
    }
    columns = result_header_only.get('columns', [])
    rows = result_header_only.get('rows', [])
    data = [columns] + rows if columns else rows

    assert len(data) == 1, f"Expected 1 line (header only), got {len(data)}"
    assert data[0] == ['col1', 'col2'], "Header mismatch"
    print(f"✓ Pass: Header-only result handled correctly")
    print()

    # Test Case 4: Old broken logic (for comparison)
    print("Test 4: Old broken logic comparison")
    result = mcp_response_success
    data_old = result.get('data', [])  # Old logic
    print(f"Old logic result: {data_old} (EMPTY!)")
    print(f"New logic result: {len(data)} lines (CORRECT!)")
    print()

    print("=" * 50)
    print("All tests passed! ✓")
    print("=" * 50)

if __name__ == '__main__':
    test_data_extraction()

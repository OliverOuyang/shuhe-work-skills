"""Test Excel multi-sheet output functionality"""

import sys
from pathlib import Path
from data_processor import (
    write_excel_multi_sheet,
    process_and_save_excel,
    ProcessingError,
    HAS_OPENPYXL,
)

# Mock CardConfig for testing
class MockCardConfig:
    def __init__(self, card_name):
        self.card_name = card_name


def test_write_excel_basic():
    """Test basic Excel writing functionality"""
    if not HAS_OPENPYXL:
        print("SKIP: openpyxl not installed")
        return

    test_data = [
        {
            "sheet_name": "测试表1",
            "headers": ["列A", "列B", "列C"],
            "rows": [
                ["数据1", "数据2", "数据3"],
                ["数据4", "数据5", "数据6"],
            ],
        },
        {
            "sheet_name": "测试表2_非常长的名字需要被截断到31个字符限制",
            "headers": ["ID", "名称", "金额"],
            "rows": [
                [1, "项目A", 1000.5],
                [2, "项目B", 2000.75],
            ],
        },
    ]

    output_path = Path("test_output.xlsx")

    try:
        write_excel_multi_sheet(output_path, test_data)
        print(f"[PASS] Excel file created: {output_path}")

        # Verify file exists
        if not output_path.exists():
            print("[FAIL] File was not created")
            return False

        # Check file size
        file_size = output_path.stat().st_size
        if file_size == 0:
            print("[FAIL] File is empty")
            return False

        print(f"[PASS] File size: {file_size} bytes")
        print("[PASS] Basic test passed")

        # Clean up
        output_path.unlink()
        print("[PASS] Test file cleaned up")

        return True

    except ProcessingError as e:
        print(f"[FAIL] ProcessingError: {e}")
        return False
    except Exception as e:
        print(f"[FAIL] Unexpected error: {e}")
        return False


def test_process_and_save_excel():
    """Test process_and_save_excel with mock data"""
    if not HAS_OPENPYXL:
        print("SKIP: openpyxl not installed")
        return

    # Mock MCP responses
    mock_responses = [
        {
            "data": {
                "data": {
                    "headers": ["日期", "渠道", "金额"],
                    "values": [
                        ["2025-01-01", "渠道A", 1000],
                        ["2025-01-02", "渠道B", 2000],
                    ],
                }
            }
        },
        {
            "data": {
                "data": {
                    "headers": ["姓名", "年龄", "分数"],
                    "values": [
                        ["张三", 25, 85.5],
                        ["李四", 30, 92.0],
                    ],
                }
            }
        },
    ]

    mock_configs = [
        MockCardConfig("卡片1_交易数据"),
        MockCardConfig("卡片2_用户信息"),
    ]

    output_dir = Path(".")
    output_filename = "test_multi_sheet.xlsx"

    try:
        result = process_and_save_excel(
            mock_responses,
            mock_configs,
            output_filename,
            output_dir,
        )

        print(f"[PASS] process_and_save_excel completed")
        print(f"  Output: {result['output_path']}")
        print(f"  Total rows: {result['total_rows']}")
        print(f"  Sheet count: {result['sheet_count']}")
        print("  Sheets:")
        for sheet in result['sheets']:
            print(f"    - {sheet['sheet_name']}: {sheet['row_count']} rows, {sheet['column_count']} cols")

        # Verify file
        output_path = Path(result['output_path'])
        if not output_path.exists():
            print("[FAIL] Output file not found")
            return False

        print("[PASS] Integration test passed")

        # Clean up
        output_path.unlink()
        print("[PASS] Test file cleaned up")

        return True

    except ProcessingError as e:
        print(f"[FAIL] ProcessingError: {e}")
        return False
    except Exception as e:
        print(f"[FAIL] Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    print("=== Testing Excel Multi-Sheet Functionality ===\n")

    if not HAS_OPENPYXL:
        print("ERROR: openpyxl is not installed")
        print("Install with: pip install openpyxl")
        sys.exit(1)

    print("Test 1: Basic write_excel_multi_sheet")
    print("-" * 50)
    test1_passed = test_write_excel_basic()
    print()

    print("Test 2: process_and_save_excel integration")
    print("-" * 50)
    test2_passed = test_process_and_save_excel()
    print()

    if test1_passed and test2_passed:
        print("=== All tests passed ===")
        sys.exit(0)
    else:
        print("=== Some tests failed ===")
        sys.exit(1)


if __name__ == "__main__":
    main()

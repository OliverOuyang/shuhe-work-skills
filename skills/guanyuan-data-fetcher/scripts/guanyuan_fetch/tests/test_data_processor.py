"""Unit tests for data_processor module"""

import pytest
import csv
from pathlib import Path
from scripts.guanyuan_fetch.data_processor import (
    parse_mcp_response,
    write_csv_utf8_bom,
    process_and_save,
    validate_csv_output,
    ProcessingError,
)


class TestParseMCPResponse:
    """Tests for MCP response parsing"""

    def test_parse_simple_response(self):
        """Test parsing a simple MCP response"""
        response = {
            "data": {
                "headers": ["日期", "金额"],
                "values": [
                    ["2025-12", 1000000],
                    ["2026-01", 1200000],
                ],
            }
        }

        headers, rows = parse_mcp_response(response)

        assert headers == ["日期", "金额"]
        assert len(rows) == 2
        assert rows[0] == ["2025-12", 1000000]

    def test_parse_dict_headers(self):
        """Test parsing response with dict headers"""
        response = {
            "data": {
                "headers": [
                    {"name": "日期", "type": "string"},
                    {"name": "金额", "type": "number"},
                ],
                "values": [["2025-12", 1000000]],
            }
        }

        headers, rows = parse_mcp_response(response)

        assert headers == ["日期", "金额"]
        assert rows == [["2025-12", 1000000]]

    def test_parse_missing_data(self):
        """Test that missing data raises ProcessingError"""
        response = {}
        with pytest.raises(ProcessingError, match="missing 'headers'"):
            parse_mcp_response(response)

    def test_parse_invalid_values(self):
        """Test that invalid values structure raises ProcessingError"""
        response = {"data": {"headers": ["col1"], "values": "not a list"}}
        with pytest.raises(ProcessingError, match="'values' must be a list"):
            parse_mcp_response(response)


class TestWriteCSVUtf8BOM:
    """Tests for CSV writing with UTF-8 BOM"""

    def test_write_csv(self, tmp_path):
        """Test writing CSV file with UTF-8 BOM"""
        output_path = tmp_path / "test.csv"
        headers = ["列1", "列2"]
        rows = [["值1", "值2"], ["值3", "值4"]]

        write_csv_utf8_bom(output_path, headers, rows)

        # Verify file exists
        assert output_path.exists()

        # Verify content
        with open(output_path, "r", encoding="utf-8-sig") as f:
            reader = csv.reader(f)
            read_rows = list(reader)

        assert read_rows[0] == headers
        assert read_rows[1:] == rows

    def test_write_csv_creates_parent_dir(self, tmp_path):
        """Test that parent directories are created"""
        output_path = tmp_path / "subdir" / "test.csv"
        headers = ["col"]
        rows = [["val"]]

        write_csv_utf8_bom(output_path, headers, rows)

        assert output_path.exists()


class TestProcessAndSave:
    """Tests for process_and_save function"""

    def test_process_and_save_success(self, tmp_path):
        """Test successful processing and saving"""
        response = {
            "data": {
                "headers": ["日期", "金额"],
                "values": [["2025-12", 1000000], ["2026-01", 1200000]],
            }
        }

        result = process_and_save(response, "test.csv", tmp_path)

        # Check result
        assert result["row_count"] == 2
        assert result["column_count"] == 2
        assert result["headers"] == ["日期", "金额"]
        assert "test.csv" in result["output_path"]

        # Check file exists
        output_path = Path(result["output_path"])
        assert output_path.exists()

    def test_process_and_save_no_rows(self, tmp_path):
        """Test that empty data raises ProcessingError"""
        response = {"data": {"headers": ["col1"], "values": []}}

        with pytest.raises(ProcessingError, match="No data rows returned"):
            process_and_save(response, "test.csv", tmp_path)


class TestValidateCSVOutput:
    """Tests for CSV validation"""

    def test_validate_existing_csv(self, tmp_path):
        """Test validation of existing CSV file"""
        csv_path = tmp_path / "test.csv"

        # Create a valid CSV
        with open(csv_path, "w", encoding="utf-8-sig", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(["header1", "header2"])
            writer.writerow(["value1", "value2"])

        # Should pass validation
        assert validate_csv_output(csv_path) is True

    def test_validate_missing_file(self, tmp_path):
        """Test that missing file raises ProcessingError"""
        csv_path = tmp_path / "nonexistent.csv"

        with pytest.raises(ProcessingError, match="CSV file not found"):
            validate_csv_output(csv_path)

    def test_validate_empty_file(self, tmp_path):
        """Test that empty file raises ProcessingError"""
        csv_path = tmp_path / "empty.csv"
        csv_path.touch()

        with pytest.raises(ProcessingError, match="CSV file is empty"):
            validate_csv_output(csv_path)

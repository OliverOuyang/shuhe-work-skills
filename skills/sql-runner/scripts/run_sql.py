#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SQL Runner Script
Executes SQL files via Dataphin MCP tools and saves results to CSV.

Usage:
    python run_sql.py <sql_file_path>

Example:
    python run_sql.py "C:\\Users\\Oliver\\Desktop\\queries\\budget_stats.sql"
"""

import sys
import os
import re
import time
import csv
import json
from datetime import datetime
from pathlib import Path

# Fix Windows console encoding for Unicode support
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')


def extract_query_name(sql_content):
    """Extract query name from SQL header comment.

    Looks for pattern: * Query Name: <name>
    Returns None if not found.
    """
    match = re.search(r'\*\s*Query Name:\s*(.+)', sql_content, re.IGNORECASE)
    if match:
        return match.group(1).strip()
    return None


def sanitize_filename(name):
    """Replace invalid filename characters with underscore. Prevents path traversal."""
    name = name.replace('..', '').replace('/', '_').replace('\\', '_')
    name = re.sub(r'^[A-Za-z]:', '', name)
    name = name.lstrip('/\\')
    sanitized = re.sub(r'[<>:"/\\|?*]+', '_', name)
    sanitized = re.sub(r'\s+', '_', sanitized)
    sanitized = sanitized.strip('_') or 'query'
    return sanitized


def call_mcp_tool(tool_name, params):
    """Call MCP tool via stdio protocol.

    This is a placeholder that should be replaced with actual MCP protocol implementation.
    In production, Claude Code will handle MCP tool invocation.
    """
    # ===================================================================
    # ⚠️  WARNING: THIS IS A MOCK IMPLEMENTATION - NOT PRODUCTION READY
    # In real usage, Claude Code calls MCP tools directly via the protocol.
    # This script is for reference/documentation purposes only.
    # ===================================================================
    print(f"[MCP] Calling tool: {tool_name}")
    print(f"[MCP] Parameters: {json.dumps(params, ensure_ascii=False, indent=2)}")

    # This would be replaced with actual MCP protocol calls
    # For now, return mock data for testing
    if tool_name == "mcp__sh_dp_mcp__submit_dp_query":
        return {
            "success": True,
            "taskId": f"dp_task_{int(time.time())}"
        }
    elif tool_name == "mcp__sh_dp_mcp__get_dp_query_status":
        # Simulate query completion after 10 seconds
        return {
            "queryStatus": "SUCCESS",
            "data": [
                ["月份", "客群", "渠道类别", "授信人数"],
                ["2026-01", "当月首登M0", "抖音", "1234"],
                ["2026-02", "存量首登M0", "腾讯", "5678"]
            ]
        }

    return {"success": False, "error": "Unknown tool"}


def submit_query(sql_content):
    """Submit SQL query to Dataphin.

    Returns:
        str: Task ID for polling

    Raises:
        RuntimeError: If submission fails
    """
    try:
        result = call_mcp_tool("mcp__sh_dp_mcp__submit_dp_query", {"sql": sql_content})

        if not result.get("success"):
            raise RuntimeError(f"Query submission failed: {result.get('error', 'Unknown error')}")

        task_id = result.get("taskId")
        if not task_id:
            raise RuntimeError("No task ID returned from submission")

        return task_id

    except Exception as e:
        raise RuntimeError(f"Failed to submit query: {str(e)}")


def poll_query_status(task_id, timeout=300, interval=5):
    """Poll query status until completion or timeout.

    Args:
        task_id: Task ID from submit_query
        timeout: Maximum wait time in seconds (default: 300 = 5 minutes)
        interval: Polling interval in seconds (default: 5)

    Returns:
        dict: Query result with 'data' field containing rows

    Raises:
        TimeoutError: If query doesn't complete within timeout
        RuntimeError: If query fails or is cancelled
    """
    start_time = time.time()
    last_status = None

    while True:
        elapsed = int(time.time() - start_time)

        if elapsed >= timeout:
            # Attempt to kill the query before raising timeout
            try:
                call_mcp_tool("mcp__sh_dp_mcp__kill_dp_query", {"taskId": task_id})
            except:
                pass
            raise TimeoutError(f"Query execution timeout after {timeout}s")

        # Poll status
        try:
            status = call_mcp_tool("mcp__sh_dp_mcp__get_dp_query_status", {"taskId": task_id})
        except Exception as e:
            raise RuntimeError(f"Failed to poll query status: {str(e)}")

        query_status = status.get("queryStatus", "UNKNOWN")

        # Only print if status changed
        if query_status != last_status:
            print(f"Query status: {query_status} ({elapsed}s)")
            last_status = query_status

        if query_status == "SUCCESS":
            return status
        elif query_status in ["FAILED", "CANCELLED"]:
            error_msg = status.get("message", "Unknown error")
            raise RuntimeError(f"Query {query_status.lower()}: {error_msg}")
        elif query_status == "RUNNING":
            # Continue polling
            pass
        else:
            # UNKNOWN or other status, continue polling
            pass

        time.sleep(interval)


def save_results(data, output_path):
    """Save query results to CSV file.

    Args:
        data: List of lists, first row is header
        output_path: Path object for output file
    """
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    # Write CSV with UTF-8 BOM for Excel compatibility
    with open(output_path, 'w', newline='', encoding='utf-8-sig') as f:
        writer = csv.writer(f)

        if not data:
            # Empty result, write empty file
            pass
        else:
            # Write all rows including header
            writer.writerows(data)

    print(f"✓ Results saved to: {output_path}")

    # Report row count
    row_count = len(data) - 1 if data else 0  # Exclude header
    print(f"✓ Total rows: {row_count}")


def main():
    """Main execution function."""
    if len(sys.argv) < 2:
        print("Error: SQL file path required")
        print("Usage: python run_sql.py <sql_file_path>")
        sys.exit(1)

    sql_file = Path(sys.argv[1])

    # Validate file exists
    if not sql_file.exists():
        print(f"Error: SQL file not found: {sql_file}")
        sys.exit(1)

    if not sql_file.is_file():
        print(f"Error: Path is not a file: {sql_file}")
        sys.exit(1)

    print(f"Reading SQL file: {sql_file}")

    # Step 1: Read SQL content
    try:
        sql_content = sql_file.read_text(encoding='utf-8')
    except Exception as e:
        print(f"Error reading SQL file: {e}")
        sys.exit(1)

    # Step 2: Extract query name
    query_name = extract_query_name(sql_content)
    if not query_name:
        query_name = sql_file.stem
        print(f"No query name found in comments, using filename: {query_name}")
    else:
        print(f"Query name: {query_name}")

    # Step 3: Submit query
    print("\n--- Submitting Query ---")
    try:
        task_id = submit_query(sql_content)
        print(f"✓ Query submitted successfully")
        print(f"Task ID: {task_id}")
    except Exception as e:
        print(f"✗ Error submitting query: {e}")
        sys.exit(1)

    # Step 4: Poll for results
    print("\n--- Polling for Results ---")
    try:
        result = poll_query_status(task_id)
        print(f"✓ Query completed successfully")
    except TimeoutError as e:
        print(f"✗ {e}")
        sys.exit(1)
    except Exception as e:
        print(f"✗ Error during query execution: {e}")
        sys.exit(1)

    # Step 5: Save results
    print("\n--- Saving Results ---")
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    sanitized_name = sanitize_filename(query_name)
    output_filename = f"{sanitized_name}_{timestamp}.csv"

    data_dir = sql_file.parent / "data"
    output_path = data_dir / output_filename

    try:
        # Extract data from MCP response
        # MCP returns data as 2D array where first row is header
        data = result.get('data', [])

        if data:
            columns = data[0] if data else []
            rows = data[1:] if len(data) > 1 else []

            # Report data size
            print(f"Columns: {len(columns)} fields")
            print(f"Data rows: {len(rows)} rows")
        else:
            print("Warning: Query returned no data")

        save_results(data, output_path)
        print(f"\n✓ Execution completed successfully")
        print(f"Output file: {output_path.absolute()}")
    except Exception as e:
        print(f"✗ Error saving results: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()

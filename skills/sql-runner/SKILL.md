---
name: sql-runner
description: Execute optimized SQL files using Dataphin MCP tools. Automatically submits queries, polls for results, and saves output to CSV with timestamped filenames. Use this skill when users mention "run SQL", "execute query", "submit to Dataphin", or want to fetch data from SQL files.
---

# SQL Runner

A skill for executing SQL queries through Dataphin's MCP interface with automatic polling and result management.

## When to Use This Skill

Use this skill when:
- User asks to "run", "execute", or "submit" a SQL file
- User wants to fetch data from Dataphin using an existing SQL query
- User mentions getting query results or data extraction
- User has optimized SQL ready to run
- User needs to automate SQL execution workflow

## What This Skill Does

1. **Read SQL File**
   - Parse SQL content from specified file path
   - Extract query name from header comments (if available)
   - Validate SQL syntax before submission

2. **Submit Query to Dataphin**
   - Use `sh_dp_mcp:submit_dp_query` tool to submit SQL
   - Obtain task ID for tracking
   - Handle submission errors gracefully

3. **Poll for Results**
   - Use `sh_dp_mcp:get_dp_query_status` to check query status
   - Poll every 5 seconds (recommended interval)
   - Timeout after 5 minutes (300 seconds)
   - Display progress to user

4. **Save Results**
   - Extract data from completed query
   - Generate filename: `{query_name}_{YYYYMMDD_HHMMSS}.csv`
   - Save to `data/` subfolder in SQL file's directory
   - Create directory if it doesn't exist

## Workflow

### Step 1: Read and Validate SQL

Read the SQL file and extract:
- Full SQL content for submission
- Query name from header comment block
- Basic syntax validation

**Expected SQL file structure**:
```sql
/*******************************************************************************
 * Query Name: Budget Core Statistics
 * Purpose: Monthly budget tracking by channel and user segment
 * ...
 ******************************************************************************/

SELECT
    ...
FROM
    ...
```

Extract "Budget Core Statistics" as the query name for filename generation.

If no header comment exists, use the SQL filename (without extension) as fallback.

### Step 2: Submit Query

Call MCP tool to submit query:

```python
result = submit_dp_query(sql=sql_content)
task_id = result['taskId']
```

Handle errors:
- Permission errors: Report to user, suggest using `apply_dp_table_permission`
- Syntax errors: Report specific error message
- Connection errors: Retry once after 3 seconds

### Step 3: Poll for Status

Poll query status with 5-second intervals:

```python
while elapsed_time < 300:  # 5 minute timeout
    status = get_dp_query_status(taskId=task_id)

    if status['queryStatus'] == 'SUCCESS':
        break
    elif status['queryStatus'] in ['FAILED', 'CANCELLED']:
        raise QueryError(status['message'])

    sleep(5)
    elapsed_time += 5
```

Display progress to user:
- "Query submitted, polling for results... (0s)"
- "Still running... (5s)"
- "Still running... (10s)"
- etc.

### Step 4: Save Results

When query succeeds:

1. Extract result data from status response
2. Generate timestamp: `datetime.now().strftime('%Y%m%d_%H%M%S')`
3. Sanitize query name for filename (replace spaces/special chars with underscore)
4. Construct filename: `{sanitized_name}_{timestamp}.csv`
5. Ensure `data/` directory exists in SQL file's parent directory
6. Write CSV with proper encoding (UTF-8 with BOM for Excel compatibility)
7. Report success with full file path

**Example output path**:
```
Input:  C:\Users\Oliver\Desktop\project\queries\budget_stats.sql
Output: C:\Users\Oliver\Desktop\project\queries\data\Budget_Core_Statistics_20260331_143022.csv
```

## Important Guidelines

**MCP Tool Integration**: The script must properly invoke MCP tools, not just mock them. The actual implementation should use the MCP protocol to call `sh_dp_mcp` tools.

**Error Handling**:
- **Permission errors**: Guide user to apply for table access
- **Syntax errors**: Show exact error line/column if available
- **Timeout**: Kill the query using `kill_dp_query` tool before exiting
- **Connection errors**: Retry submission once before failing

**File Naming**:
- Always use timestamp to prevent overwriting
- Sanitize query name (remove spaces, special characters)
- Preserve Chinese characters in query name if present
- Use `.csv` extension (not `.xlsx`)

**CSV Format**:
- Use UTF-8 with BOM for Excel compatibility
- Include header row
- Handle null values as empty strings
- Escape commas and quotes properly

**Progress Display**:
- Show polling intervals clearly
- Display elapsed time
- Don't flood console (max 1 message per 5 seconds)

## Edge Cases

**Very Long Queries**: If query runs longer than 5 minutes, increase timeout or implement cancellation logic.

**Large Result Sets**: Dataphin limits to 10,000 rows. If result is truncated, warn user and suggest using data export tools.

**Multiple SQL Statements**: If file contains multiple queries separated by semicolons, execute them sequentially and save separate CSV files.

**Variables in SQL**: The SQL may contain `${bizdate}` placeholders. These should be preserved as-is when submitting to Dataphin (the platform will substitute them).

**Empty Results**: If query returns zero rows, still create the CSV with just the header row and notify user.

## Known Limitations

Based on boundary testing, this skill has the following limitations:

1. **Maximum Result Size**: Dataphin enforces a hard limit of 10,000 rows per query. If your result set exceeds this, the data will be truncated. Use filtering or data export tools for larger datasets.

2. **Timeout Enforcement**: Queries that run longer than 5 minutes (300 seconds) will be automatically killed. Very complex queries may need optimization or a custom timeout configuration.

3. **File Path Constraints**:
   - Paths with spaces are supported and handled correctly
   - Paths with Chinese characters are supported (UTF-8)
   - Maximum path length varies by OS (255 chars on most systems)

4. **Query Name Sanitization**:
   - Special characters `< > : " / \ | ? *` are replaced with underscore
   - Spaces are converted to underscores
   - Chinese characters are preserved
   - Query names longer than ~200 chars may cause issues with file systems

5. **Status Update Frequency**: Status is only printed when it changes, not every 5 seconds. This reduces console spam but means status updates may not appear if the query status remains constant.

6. **Network Resilience**: Single connection failures during polling are not retried. Network interruptions lasting >5 seconds between polls may cause query abandonment.

7. **CSV Size**: While result rows are limited to 10,000, very wide tables (1000+ columns) may create large CSV files (>100MB).

## Data Extraction & CSV Format

This skill extracts data from Dataphin queries and formats it as CSV with these specifications:

**Data Structure**:
- Results returned as list of lists: `[[header1, header2, ...], [row1_val1, row1_val2, ...], ...]`
- First row is always treated as the header row
- Data rows contain string values
- Empty/null values are represented as empty strings

**CSV Encoding & Format**:
- Encoding: UTF-8 with BOM (utf-8-sig)
- BOM prefix ensures Excel opens the file correctly and recognizes encoding
- Line endings: LF (Unix-style, compatible with Excel)
- Delimiter: Comma (,)
- Quote character: Double quote (")
- Escape method: Double quote escaping

**Filename Generation**:
```
{sanitized_query_name}_{timestamp}.csv
Timestamp format: YYYYMMDD_HHMMSS (e.g., 20260331_143022)
Example: Budget_Core_Statistics_20260331_143022.csv
```

**Directory Structure**:
```
Input SQL:  C:\Projects\queries\budget_stats.sql
Output CSV: C:\Projects\queries\data\Budget_Core_Statistics_20260331_143022.csv
            └─ Created in "data/" subdirectory relative to SQL file location
```

**Empty Result Handling**:
- If query returns 0 data rows, CSV is created with header row only
- Row count reported as 0
- File still created to indicate successful query execution

## Error Handling Enhancements

This skill implements robust error handling across multiple scenarios:

**Permission Errors**:
- Detected when Dataphin returns permission/authorization errors
- User is prompted with: "You don't have access to the required tables"
- Suggestion provided: "Use `apply_dp_table_permission` to request table access"
- Execution stops immediately, no output file created
- Exit code: 1 (failure)

**Syntax Errors**:
- Detected when SQL parsing fails in Dataphin
- Full error message displayed to user with details if available
- Line number and column information included when provided by Dataphin
- No output file created
- Exit code: 1 (failure)

**Timeout Handling**:
- Query automatically killed after 300 seconds (5 minutes)
- `kill_dp_query` MCP tool called before exiting
- User receives clear timeout message with elapsed time
- Prevents resource waste on Dataphin side
- Exit code: 1 (failure)

**Connection Errors During Submission**:
- Initial submission failure triggers error report
- Single retry logic (future enhancement)
- If both attempts fail, user sees submission error
- Exit code: 1 (failure)

**Status Polling Failures**:
- If poll request fails during execution, error is reported
- Query may continue running on Dataphin side
- Manual kill via `kill_dp_query` may be needed
- Exit code: 1 (failure)

**File System Errors**:
- Directory creation failures are caught and reported
- File write permissions issues generate clear error message
- Path validation occurs before query submission
- Exit code: 1 (failure)

## Usage Precautions

**Before Running Queries**:

1. **Check Query Performance**: Very complex queries with many JOINs or aggregations may timeout. Test locally or with LIMIT 100 first.

2. **Verify Table Permissions**: If you're unsure about access, check permissions before running. Permission errors stop execution immediately.

3. **Monitor Result Size**: Be aware of how many rows your query returns. 10,000-row limit is enforced by Dataphin.

4. **Handle Chinese Characters**: Query names and file paths with Chinese characters work correctly, but ensure your terminal supports UTF-8 output.

5. **Plan for Long Queries**: Queries running longer than 5 minutes will timeout. Consider optimizing SQL or increasing timeout if needed.

**During Query Execution**:

1. **Progress Monitoring**: Status updates appear when query status changes (RUNNING → SUCCESS or FAILED), not every 5 seconds. Be patient.

2. **Don't Interrupt**: The skill handles timeouts automatically. Let it complete rather than manually stopping.

3. **Network Stability**: Maintain stable network connection during polling. Disconnections >5 seconds may cause issues.

**After Query Completion**:

1. **Verify Output**: Check that the CSV file was created in `data/` subdirectory with correct naming and data.

2. **Excel Compatibility**: CSV is UTF-8 with BOM, so it opens directly in Excel. No conversion needed.

3. **Timestamp Uniqueness**: Each run creates a new file with current timestamp. Old results are never overwritten (unless you manually delete them).

4. **Large Files**: If result set is large (>50MB), Excel may be slow opening it. Consider using dedicated CSV viewers for analysis.

## Success Criteria

A successful execution should:
- Submit SQL without errors
- Poll status without flooding logs
- Save results with proper filename format
- Create `data/` directory if needed
- Report clear error messages on failure
- Complete within timeout period
- Generate valid CSV readable by Excel

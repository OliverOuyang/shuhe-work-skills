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

## Success Criteria

A successful execution should:
- Submit SQL without errors
- Poll status without flooding logs
- Save results with proper filename format
- Create `data/` directory if needed
- Report clear error messages on failure
- Complete within timeout period
- Generate valid CSV readable by Excel

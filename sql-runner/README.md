# SQL Runner

Execute SQL files through Dataphin MCP interface with automatic result management.

## Installation

The skill is automatically available through Claude Code. No installation required.

## Usage

### Command Line

```bash
python ~/.claude/skills/sql-runner/scripts/run_sql.py <sql_file_path>
```

### Example

```bash
python ~/.claude/skills/sql-runner/scripts/run_sql.py "C:\Users\Oliver\Desktop\queries\budget_stats.sql"
```

### Through Claude

Simply ask:
- "Run this SQL file: [path]"
- "Execute query from [path]"
- "Submit SQL to Dataphin: [path]"

## How It Works

1. **Reads SQL file** and extracts query name from header comments
2. **Submits to Dataphin** using MCP tools
3. **Polls for completion** every 5 seconds (max 5 minutes)
4. **Saves results** to `data/` subfolder with timestamped filename

## Output Format

Results are saved as:
```
<sql_directory>/data/<query_name>_<YYYYMMDD_HHMMSS>.csv
```

Example:
```
Input:  C:\Users\Oliver\Desktop\queries\budget_stats.sql
Output: C:\Users\Oliver\Desktop\queries\data\Budget_Core_Statistics_20260331_143022.csv
```

## SQL File Format

For best results, include a header comment with query name:

```sql
/*******************************************************************************
 * Query Name: Budget Core Statistics
 * Purpose: Monthly budget tracking by channel and user segment
 * ...
 ******************************************************************************/

SELECT ...
```

If no header is found, the filename is used as the query name.

## Error Handling

The script handles:
- **Permission errors**: Reports error and suggests applying for table access
- **Syntax errors**: Shows specific error message
- **Timeout**: Cancels query after 5 minutes
- **Connection errors**: Retries once before failing

## Requirements

- Python 3.7+
- Access to Dataphin through MCP tools
- Appropriate table permissions

## Integration with Other Skills

Works well with:
- **sql-optimizer**: Optimize SQL before running
- **data-analysis**: Analyze results after query completes
- **dp-explorer**: Explore tables before writing queries

## Limitations

- Maximum 10,000 rows per query (Dataphin limit)
- 5-minute timeout for long-running queries
- Only supports SELECT statements
- Results saved as CSV only (not XLSX)

## Troubleshooting

**Query timeout**: Increase timeout in script or optimize SQL query

**Permission denied**: Apply for table access using `apply_dp_table_permission`

**Empty results**: Check SQL logic and date filters

**File not found**: Verify SQL file path is correct and file exists

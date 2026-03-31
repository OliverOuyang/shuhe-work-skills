---
name: sql-optimizer
description: Optimize and clean SQL queries with structured comments, format improvements, and syntax validation. Use this skill whenever users mention "optimize SQL", "clean SQL", "add comments to SQL", "format SQL", "refactor SQL", or want to improve SQL readability. Specifically designed for Hive/MaxCompute SQL with support for variables like ${bizdate}, partitioning, and window functions.
---

# SQL Optimizer

A skill for optimizing and cleaning Hive/MaxCompute SQL queries with enterprise-grade formatting and documentation standards.

## When to Use This Skill

Use this skill when:
- User asks to "optimize", "clean", "format", or "refactor" SQL code
- User wants to add comments or documentation to SQL
- User mentions improving SQL readability or maintainability
- User has messy SQL with duplicate queries or excessive commented code
- User needs SQL standardized for team collaboration

## What This Skill Does

1. **Remove Redundancy**
   - Eliminate duplicate queries
   - Clean up commented-out code (while preserving important notes)
   - Remove unused CTEs or subqueries

2. **Add Structured Documentation**
   - File header with query metadata (name, purpose, granularity, data range, update frequency)
   - Section headers for dimensions, metrics, filters, and grouping
   - Inline comments for complex logic
   - Footer with glossary of business terms and technical notes

3. **Improve Formatting**
   - Consistent indentation and alignment
   - Logical grouping of SELECT fields
   - Clear CASE statement formatting
   - Readable JOIN conditions

4. **Validate Syntax**
   - Check SQL syntax for Hive/MaxCompute compatibility
   - Verify variable usage (${bizdate}, ${pt} etc.)
   - Ensure partition references are valid
   - Report any syntax errors before saving

## Workflow

### Step 1: Read and Analyze

Read the SQL file and identify:
- Duplicate queries or CTEs
- Commented code blocks (determine if they're notes or dead code)
- Missing documentation
- Formatting inconsistencies
- Business logic patterns (conversions, aggregations, filters)

### Step 2: Structure the Optimization

Organize the optimized SQL with this structure:

```sql
/*******************************************************************************
 * Query Name: [Descriptive name based on what it does]
 * Purpose: [What business question this answers]
 * Granularity: [Row-level grain, e.g., "date + channel + platform + asset_type"]
 * Data Range: [Time window, e.g., "2026-03-01 onwards (configurable)"]
 * Update Frequency: [Daily, weekly, etc.]
 ******************************************************************************/

SELECT
    -- ==================== Dimension Fields ====================
    [dimensions with inline comments]

    -- ==================== Metric Fields: [Category Name] ====================
    [metrics grouped by category with inline comments]

    -- ==================== Derived Fields ====================
    [calculated fields]

FROM
    [main table with description]

    -- [Describe the join]
    LEFT/INNER JOIN [joined table]
        ON [join conditions]

WHERE
    -- [Explain the filter logic]
    [filter conditions]

GROUP BY
    -- [Explain grouping logic]
    [grouping fields]

ORDER BY
    [ordering]
;

/*******************************************************************************
 * Glossary and Notes:
 *
 * [Business Term Definitions]:
 * - T0: [definition]
 * - Conversion funnel: [stages]
 *
 * [Technical Notes]:
 * - [Important caveats, assumptions, or edge cases]
 ******************************************************************************/
```

### Step 3: Apply Formatting Rules

**SELECT Clause**:
- Group related fields together with section headers
- Align AS aliases vertically when practical
- Keep CASE statements indented consistently
- Use descriptive Chinese aliases for business metrics if original uses them

**CASE Statements**:
```sql
CASE
    WHEN condition1 THEN 'result1'
    WHEN condition2 THEN 'result2'
    ELSE 'default'
END AS field_name
```

**Aggregations**:
```sql
SUM(IF(condition, field, 0)) AS metric_name,  -- Inline comment explaining the metric
```

**Joins**:
- Put join type (LEFT/INNER) on same line as JOIN keyword
- Indent ON conditions
- Add comment above join explaining its purpose

**WHERE/GROUP BY**:
- One condition per line for complex filters
- Add comments for non-obvious conditions
- In GROUP BY, reference fields explicitly (not by position)

### Step 4: Validate Syntax

Run the validation script to check:
- Basic SQL syntax (SELECT, FROM, WHERE, GROUP BY order)
- Hive/MaxCompute specific syntax (functions, variables)
- Balanced parentheses and quotes
- Valid partition references

Execute:
```bash
python ~/.claude/skills/sql-optimizer/scripts/validate_sql.py <sql_file_path>
```

If validation fails, fix the errors and re-validate before proceeding.

### Step 5: Save and Report

1. Overwrite the original SQL file with optimized version
2. Report to user:
   - Summary of changes (e.g., "Removed 1 duplicate query, added 45 inline comments")
   - Validation status
   - File location
   - Quick preview of the structure

## Important Guidelines

**Preserve Business Logic**: Never change the query results. All optimizations are cosmetic or structural only.

**Handle Comments Intelligently**:
- Keep comments that explain WHY (business context, edge cases)
- Remove comments that just repeat WHAT the code does
- Remove large blocks of commented-out code unless they're marked as "TODO" or "Future enhancement"

**Chinese vs English**:
- Preserve the original language choice for field aliases
- Use Chinese for business terms if original SQL uses Chinese
- Keep technical comments in Chinese if that's the project convention

**Hive/MaxCompute Specifics**:
- Recognize partition variables: `${bizdate}`, `${pt}`, `${yyyymmdd}`
- Preserve partition predicates (ds =, pt =)
- Don't rewrite Hive-specific functions (e.g., `date_sub`, `substr`, `to_date`)
- Keep window functions formatted clearly

**Error Handling**:
- If SQL syntax is severely broken, report the errors and ask user to provide a working version first
- If validation script fails to run, fall back to basic manual syntax checks

## Edge Cases

**Multiple Queries in One File**: Optimize each query separately, add divider comments between them.

**Extremely Long Queries**: Break into sections with clear headers, consider suggesting CTE refactoring.

**Performance Optimization**: This skill focuses on readability. If user asks about performance (e.g., "make it faster"), acknowledge that's a different scope and focus only on formatting unless they explicitly want performance tuning too.

## Example Transformation

**Before**:
```sql
select
--substr(a.date_key,1,7) as date_month,
a.date_key,
 b.first_login_platform_api_app_mp as platform,
case
     when b.marketing_channel_group_name ='精准营销' then '精准营销'
     when b.marketing_channel_group_name in ('抖音','抖音二组') then '抖音'
     else '其他' end as 渠道类别,
sum(a.first_login_user_count) as log_num,
sum(a.login_t0_apply_finish_user_count) as t0_ato_num-- T0申完户
from
(select * from dwt.table1 where ds = '${bizdate}') a
LEFT JOIN dwt.table2 b on a.uid=b.uid and b.ds = '${bizdate}'
where to_date(a.date_key)>='2026-03-01'
group BY a.date_key, b.first_login_platform_api_app_mp, [case statement]
```

**After**:
```sql
/*******************************************************************************
 * Query Name: Channel Conversion Metrics
 * Purpose: Daily conversion funnel metrics by channel and platform
 * Granularity: date + platform + channel_category
 * Data Range: 2026-03-01 onwards
 * Update Frequency: Daily
 ******************************************************************************/

SELECT
    -- ==================== Dimensions ====================
    a.date_key,                                             -- Date
    b.first_login_platform_api_app_mp AS platform,         -- First login platform

    -- Channel category aggregation
    CASE
        WHEN b.marketing_channel_group_name = '精准营销' THEN '精准营销'
        WHEN b.marketing_channel_group_name IN ('抖音', '抖音二组') THEN '抖音'
        ELSE '其他'
    END AS 渠道类别,

    -- ==================== Metrics: Conversion Funnel ====================
    SUM(a.first_login_user_count) AS log_num,              -- First login users
    SUM(a.login_t0_apply_finish_user_count) AS t0_ato_num  -- T0 application complete users

FROM
    -- User daily conversion index fact table
    (
        SELECT *
        FROM dwt.table1
        WHERE ds = '${bizdate}'
    ) a

    -- Left join user comprehensive info dimension table
    LEFT JOIN dwt.table2 b
        ON a.uid = b.uid
        AND b.ds = '${bizdate}'

WHERE
    -- Data range filter: from 2026-03-01
    TO_DATE(a.date_key) >= '2026-03-01'

GROUP BY
    a.date_key,
    b.first_login_platform_api_app_mp,
    CASE
        WHEN b.marketing_channel_group_name = '精准营销' THEN '精准营销'
        WHEN b.marketing_channel_group_name IN ('抖音', '抖音二组') THEN '抖音'
        ELSE '其他'
    END
;

/*******************************************************************************
 * Glossary:
 * - T0: Same day as first login
 * - log: Login event
 * - ato: Application To (complete)
 ******************************************************************************/
```

## Success Criteria

An optimized SQL should:
- Be immediately understandable to a new team member
- Have clear section markers for quick navigation
- Preserve exact business logic (same query results)
- Pass syntax validation
- Follow consistent formatting throughout
- Include helpful inline comments where logic is non-obvious

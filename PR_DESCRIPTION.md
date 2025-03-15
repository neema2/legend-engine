# Add timeslice function to Legend Engine Pure language with DuckDB and Snowflake support

This PR adds a new 'timeslice' function to Legend Engine's Pure language with support for both DuckDB and Snowflake.

## Changes
- Added Pure function definition in dateExtension.pure
- Created PCT tests for the timeslice function
- Implemented Java reference implementations (compiled and interpreted)
- Added database-specific implementations:
  - DuckDB implementation using time_bucket function
  - Snowflake implementation using timeslice function
- Added function registry entries

## References
- DuckDB time_bucket docs: https://duckdb.org/docs/stable/sql/functions/date.html
- Snowflake timeslice docs: https://docs.snowflake.com/en/sql-reference/functions/time_slice
- Similar implementation PR: https://github.com/finos/legend-engine/pull/3162

Link to Devin run: https://app.devin.ai/sessions/5b4129d0f33f4c85b7f2fc5d96b98600
Requested by: Neema.Raphael@gs.com

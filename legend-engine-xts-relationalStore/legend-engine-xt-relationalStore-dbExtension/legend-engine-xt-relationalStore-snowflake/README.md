# Legend Engine Snowflake Extension

This module provides Snowflake-specific extensions for the Legend Engine.

## Map Functions

The Snowflake extension includes support for map operations using Snowflake's native map functions:

### Map Insert Function

The `mapInsert` function allows inserting a key-value pair into a map, leveraging Snowflake's native `MAP_INSERT` function:

```
function <<functionType.NativeFunction>> meta::relational::functions::snowflake::mapInsert<U,V>(map:Map<U,V>[1], key:U[1], value:V[1]):Map<U,V>[1]
```

This function is implemented using Snowflake's `MAP_INSERT` function, which has the following syntax:

```sql
MAP_INSERT(<map_expr>, <key_expr>, <value_expr>)
```

The function returns a new map with the key-value pair added. If the key already exists in the map, its value is replaced with the new value.

For more information on Snowflake's MAP_INSERT function, see the [Snowflake documentation](https://docs.snowflake.com/en/sql-reference/functions/map_insert).

## Implementation Details

The implementation follows the pattern established in the [AsOfJoin PR (#3162)](https://github.com/finos/legend-engine/pull/3162), which includes:

1. Pure Language Definition:
   - The native function signature already exists in `put.pure`
   - No changes needed to the signature

2. Java Implementations:
   - Already exist in both compiled and interpreted modes
   - No changes needed to the core implementations

3. Database-specific Extensions:
   - Snowflake: Created extension using Snowflake's MAP_INSERT function
     - Signature: `MAP_INSERT(<map_expr>, <key_expr>, <value_expr>)`
     - Implementation generates appropriate SQL for Snowflake

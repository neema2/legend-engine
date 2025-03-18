# Adding New Functions to Legend Engine

This documentation provides a comprehensive guide on how to add new functions to the Legend Engine, using the timeSlice function implementation as a practical example.

## Overview

Adding a new function to Legend Engine requires implementing several components across different layers of the architecture:

1. **Pure Language Definition**: Define the function signature in Pure language
2. **Java Reference Implementations**: 
   - Compiled mode implementation
   - Interpreted mode implementation
3. **Database-Specific Implementations**: For each supported database (e.g., DuckDB, Snowflake)
4. **Test Suite**: Comprehensive tests using the PCT (Parameterized Compatibility Testing) framework

## Step 1: Define the Function in Pure Language

Create a new Pure file or modify an existing one to define the function signature. The file should be placed in the appropriate module based on the function's category.

**Example**: For the timeSlice function, we created a new file at:
```
legend-engine-core/legend-engine-core-pure/legend-engine-pure-code-functions-relation/legend-engine-pure-functions-relation-pure/src/main/resources/core_functions_relation/relation/functions/transformation/timeslice.pure
```

The function definition includes:
- Function signatures with appropriate parameters
- PCT annotations to mark the function for testing
- Documentation comments

```pure
// Basic timeSlice function that takes a timestamp and time unit
native function <<PCT.function>> meta::pure::functions::relation::timeSlice(timestamp:DateTime[1], timeUnit:String[1]):DateTime[1];

// timeSlice with slice size parameter
native function <<PCT.function>> meta::pure::functions::relation::timeSlice(timestamp:DateTime[1], timeUnit:String[1], sliceSize:Integer[1]):DateTime[1];

// timeSlice with slice size and end of slice parameters
native function <<PCT.function>> meta::pure::functions::relation::timeSlice(timestamp:DateTime[1], timeUnit:String[1], sliceSize:Integer[1], endOfSlice:Boolean[1]):DateTime[1];


```

## Step 2: Implement Java Reference Implementations

### 2.1 Compiled Mode Implementation

Create a Java class in the compiled functions module for the new function:

**Example**: For timeSlice, we created:
```
legend-engine-core/legend-engine-core-pure/legend-engine-pure-code-functions-relation/legend-engine-pure-runtime-java-extension-compiled-functions-relation/src/main/java/org/finos/legend/pure/runtime/java/extension/external/relation/compiled/natives/TimeSlice.java
```

```java
public class TimeSlice extends AbstractNative implements Native
{
    public TimeSlice()
    {
        super(
            "timeSlice_DateTime_1__String_1__DateTime_1_",
            "timeSlice_DateTime_1__String_1__Integer_1__DateTime_1_",
            "timeSlice_DateTime_1__String_1__Integer_1__Boolean_1__DateTime_1_",
            "timeSlice_DateTime_1__String_1__Integer_1__Boolean_1__String_1__DateTime_1_"
        );
    }

    @Override
    public String build(CoreInstance topLevelElement, CoreInstance functionExpression, ListIterable<String> transformedParams, ProcessorContext processorContext)
    {
        StringBuilder result = new StringBuilder("org.finos.legend.pure.runtime.java.extension.external.relation.compiled.RelationNativeImplementation.timeSlice");
        result.append('(');
        
        // Add parameters
        result.append(transformedParams.get(0));
        result.append(", ");
        result.append(transformedParams.get(1));
        
        // Add optional parameters if present
        if (transformedParams.size() > 2)
        {
            result.append(", ");
            result.append(transformedParams.get(2));
            
            if (transformedParams.size() > 3)
            {
                result.append(", ");
                result.append(transformedParams.get(3));
                
                if (transformedParams.size() > 4)
                {
                    result.append(", ");
                    result.append(transformedParams.get(4));
                }
            }
        }
        
        result.append(", ");
        result.append("es)");
        return result.toString();
    }
}
```

### 2.2 Add Implementation to RelationNativeImplementation

Implement the actual function logic in the RelationNativeImplementation class:

```java
// In RelationNativeImplementation.java
public static PureDate timeSlice(PureDate timestamp, String timeUnit, ExecutionSupport es)
{
    return timeSlice(timestamp, timeUnit, 1, false, null, es);
}

public static PureDate timeSlice(PureDate timestamp, String timeUnit, long sliceSize, ExecutionSupport es)
{
    return timeSlice(timestamp, timeUnit, sliceSize, false, null, es);
}

public static PureDate timeSlice(PureDate timestamp, String timeUnit, long sliceSize, boolean endOfSlice, ExecutionSupport es)
{
    return timeSlice(timestamp, timeUnit, sliceSize, endOfSlice, null, es);
}

public static PureDate timeSlice(PureDate timestamp, String timeUnit, long sliceSize, boolean endOfSlice, ExecutionSupport es)
{
    // Implementation logic here
    // ...
}
```

### 2.3 Interpreted Mode Implementation

Create a detailed implementation for interpreted mode that handles all the function logic:

**Example**: For timeSlice, we created:
```
legend-engine-core/legend-engine-core-pure/legend-engine-pure-code-functions-relation/legend-engine-pure-runtime-java-extension-interpreted-functions-relation/src/main/java/org/finos/legend/pure/runtime/java/extension/external/relation/interpreted/natives/TimeSlice.java
```

The interpreted implementation includes:

```java
public class TimeSlice extends Shared
{
    public TimeSlice(FunctionExecutionInterpreted functionExecution, ModelRepository repository)
    {
        super(functionExecution, repository);
    }

    @Override
    public CoreInstance execute(ListIterable<? extends CoreInstance> params, Stack<MutableMap<String, CoreInstance>> resolvedTypeParameters, Stack<MutableMap<String, CoreInstance>> resolvedMultiplicityParameters, VariableContext variableContext, CoreInstance functionExpressionToUseInStack, Profiler profiler, InstantiationContext instantiationContext, ExecutionSupport executionSupport, Context context, ProcessorSupport processorSupport) throws PureExecutionException
    {
        // Extract timestamp parameter
        CoreInstance timestampParam = Instance.getValueForMetaPropertyToOneResolved(params.get(0), M3Properties.values, processorSupport);
        ZonedDateTime timestamp = ((DateCoreInstance)timestampParam).getValue().getZonedDateTime();
        
        // Extract time unit parameter
        CoreInstance timeUnitParam = Instance.getValueForMetaPropertyToOneResolved(params.get(1), M3Properties.values, processorSupport);
        String timeUnit = timeUnitParam.getName().toUpperCase();
        
        // Extract optional parameters and implement time slicing logic
        // ...
    }
    
    // Helper methods for different time unit truncations
    private ZonedDateTime truncateToSecond(ZonedDateTime timestamp, int sliceSize) { ... }
    private ZonedDateTime truncateToMinute(ZonedDateTime timestamp, int sliceSize) { ... }
    private ZonedDateTime truncateToHour(ZonedDateTime timestamp, int sliceSize) { ... }
    // ...
}
```

The interpreted implementation contains the full logic for time slicing with different time units and supporting the end-of-slice parameter.

## Step 3: Implement Database-Specific Versions

For each supported database, implement the function using native database features when available.

### 3.1 DuckDB Implementation

For DuckDB, we modified:
```
legend-engine-xts-relationalStore/legend-engine-xt-relationalStore-dbExtension/legend-engine-xt-relationalStore-duckdb/legend-engine-xt-relationalStore-duckdb-pure/src/main/resources/core_relational_duckdb/relational/sqlQueryToString/duckdbExtension.pure
```

We added the following entries to the dynaFnToSql list:

```pure
dynaFnToSql('timeSlice', $allStates, ^ToSql(format='time_bucket(%s, %s)', transform={p:String[2] | constructIntervalFunction('\'1 ' + $p->at(1)->toLower() + '\'', '1') + ', ' + $p->at(0)})),
dynaFnToSql('timeSlice', $allStates, ^ToSql(format='time_bucket(%s, %s)', transform={p:String[3] | constructIntervalFunction('\''+$p->at(2)+' ' + $p->at(1)->toLower() + '\'', '1') + ', ' + $p->at(0)})),
dynaFnToSql('timeSlice', $allStates, ^ToSql(format='%s', transform={p:String[4] | if($p->at(3) == 'true', 
                                                                                | 'time_bucket(' + constructIntervalFunction('\''+$p->at(2)+' ' + $p->at(1)->toLower() + '\'', '1') + ', ' + $p->at(0) + ') + ' + constructIntervalFunction('\''+$p->at(2)+' ' + $p->at(1)->toLower() + '\'', '1'),
                                                                                | 'time_bucket(' + constructIntervalFunction('\''+$p->at(2)+' ' + $p->at(1)->toLower() + '\'', '1') + ', ' + $p->at(0) + ')')})),

```

This implementation uses DuckDB's native `time_bucket` function, which provides better performance and accuracy than a generic implementation.

## Step 4: Create PCT Tests

Create comprehensive tests using the PCT framework to verify the function works correctly across all implementations.

**Example**: For timeSlice, we added tests to the same Pure file:

```pure
function <<PCT.test>> meta::pure::functions::relation::tests::timeSlice::testBasicTimeSlice<T|m>(f:Function<{Function<{->T[m]}>[1]->T[m]}>[1]):Boolean[1]
{
    let tds = #TDS
                timestamp
                2023-01-15T14:30:45.123+0000
            #;
    
    // Test with different time units
    let yearExpr = {|$tds->extend([col(x|timeSlice($x.timestamp, 'YEAR'), 'yearResult')])};
    let quarterExpr = {|$tds->extend([col(x|timeSlice($x.timestamp, 'QUARTER'), 'quarterResult')])};
    let monthExpr = {|$tds->extend([col(x|timeSlice($x.timestamp, 'MONTH'), 'monthResult')])};
    // ... more test cases
    
    let yearRes = $f->eval($yearExpr);
    // ... evaluate other expressions
    
    assertEquals(%2023-01-01T00:00:00.000+0000, $yearRes.rows->at(0).get('yearResult'));
    // ... more assertions
    
    true;
}
```

Key aspects of PCT tests:
1. Use the `<<PCT.test>>` annotation
2. Take a Function parameter to allow testing across different implementations
3. Use TDSs (Tabular Data Sets) for test data
4. Test all function signatures and edge cases

## Step 5: Register the Function in the PCT Framework

Ensure the function is properly registered in the PCT framework:

1. Add the function to the appropriate PCTReportProvider class
2. Configure the PCT test in the pom.xml file

## Step 6: Run PCT Tests

Run the PCT tests to verify the implementation:

```bash
mvn test -pl legend-engine-xts-relationalStore/legend-engine-xt-relationalStore-dbExtension/legend-engine-xt-relationalStore-duckdb/legend-engine-xt-relationalStore-duckdb-PCT -Dtest=Test_Relational_DuckDB_RelationFunctions_PCT
```

## Best Practices

1. **Research Database Features**: Before implementing, research the native database functions available in each supported database to optimize performance.

2. **Consistent Naming**: Follow the naming conventions used in the codebase.

3. **Complete Documentation**: Document the function behavior, parameters, and return values.

4. **Comprehensive Testing**: Test all function signatures and edge cases.

5. **Error Handling**: Implement proper error handling for invalid inputs.

6. **Performance Considerations**: Consider performance implications, especially for functions that will be used in large datasets.

## Conclusion

Adding a new function to Legend Engine involves multiple steps across different layers of the architecture. By following this guide and using the timeSlice implementation as a reference, you can successfully add new functions to the Legend Engine.

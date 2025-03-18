// Copyright 2024 Goldman Sachs
//
// Licensed under the Apache License, Version 2.0 (the "License");
// you may not use this file except in compliance with the License.
// You may obtain a copy of the License at
//
//      http://www.apache.org/licenses/LICENSE-2.0
//
// Unless required by applicable law or agreed to in writing, software
// distributed under the License is distributed on an "AS IS" BASIS,
// WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
// See the License for the specific language governing permissions and
// limitations under the License.

package org.finos.legend.pure.runtime.java.extension.external.relation.interpreted.natives;

import org.eclipse.collections.api.list.ListIterable;
import org.eclipse.collections.api.map.MutableMap;
import org.finos.legend.pure.m3.compiler.Context;
import org.finos.legend.pure.m3.exception.PureExecutionException;
import org.finos.legend.pure.m3.navigation.Instance;
import org.finos.legend.pure.m3.navigation.M3Properties;
import org.finos.legend.pure.m3.navigation.ProcessorSupport;
import org.finos.legend.pure.m3.navigation.ValueSpecificationBootstrap;
import org.finos.legend.pure.m4.ModelRepository;
import org.finos.legend.pure.m4.coreinstance.CoreInstance;
import org.finos.legend.pure.m4.coreinstance.primitive.DateCoreInstance;
import org.finos.legend.engine.plan.dependencies.domain.date.DurationUnit;
import org.finos.legend.pure.runtime.java.extension.external.relation.interpreted.natives.shared.Shared;
import org.finos.legend.pure.runtime.java.interpreted.ExecutionSupport;
import org.finos.legend.pure.runtime.java.interpreted.FunctionExecutionInterpreted;
import org.finos.legend.pure.runtime.java.interpreted.VariableContext;
import org.finos.legend.pure.runtime.java.interpreted.natives.InstantiationContext;
import org.finos.legend.pure.runtime.java.interpreted.profiler.Profiler;

import java.time.ZoneId;
import java.time.ZonedDateTime;
import java.time.temporal.ChronoUnit;
import java.util.Stack;

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
        DurationUnit timeUnit = DurationUnit.valueOf(timeUnitParam.getName());
        
        // Extract optional slice size parameter (default to 1)
        int sliceSize = 1;
        if (params.size() > 2)
        {
            CoreInstance sliceSizeParam = Instance.getValueForMetaPropertyToOneResolved(params.get(2), M3Properties.values, processorSupport);
            sliceSize = Integer.parseInt(sliceSizeParam.getName());
        }
        
        // Extract optional end of slice parameter (default to false)
        boolean endOfSlice = false;
        if (params.size() > 3)
        {
            CoreInstance endOfSliceParam = Instance.getValueForMetaPropertyToOneResolved(params.get(3), M3Properties.values, processorSupport);
            endOfSlice = Boolean.parseBoolean(endOfSliceParam.getName());
        }
        
        // Always use UTC as the default timezone
        ZoneId timezone = ZoneId.of("UTC");
        
        // Convert timestamp to UTC timezone
        ZonedDateTime timestampInTimezone = timestamp.withZoneSameInstant(timezone);
        
        // Calculate time slice
        ZonedDateTime result = calculateTimeSlice(timestampInTimezone, timeUnit, sliceSize, endOfSlice);
        
        // Convert result back to original timezone
        ZonedDateTime resultInOriginalTimezone = result.withZoneSameInstant(timestamp.getZone());
        
        // Create and return result
        DateCoreInstance dateInstance = (DateCoreInstance) repository.newCoreInstance("", processorSupport.package_getByUserPath("meta::pure::metamodel::type::DateTime"), null);
        dateInstance.setValue(resultInOriginalTimezone);
        return ValueSpecificationBootstrap.wrapValueSpecification(dateInstance, false, processorSupport);
    }
    
    private ZonedDateTime calculateTimeSlice(ZonedDateTime timestamp, DurationUnit timeUnit, int sliceSize, boolean endOfSlice)
    {
        ZonedDateTime result;
        
        switch (timeUnit)
        {
            case SECONDS:
                result = truncateToSecond(timestamp, sliceSize);
                break;
            case MINUTES:
                result = truncateToMinute(timestamp, sliceSize);
                break;
            case HOURS:
                result = truncateToHour(timestamp, sliceSize);
                break;
            case DAYS:
                result = truncateToDay(timestamp);
                break;
            case WEEKS:
                result = truncateToWeek(timestamp);
                break;
            case MONTHS:
                result = truncateToMonth(timestamp);
                break;
            case QUARTERS:
                result = truncateToQuarter(timestamp);
                break;
            case YEARS:
                result = truncateToYear(timestamp);
                break;
            default:
                throw new PureExecutionException("Unsupported time unit: " + timeUnit);
        }
        
        // If end of slice is requested, add the slice size to the result
        if (endOfSlice)
        {
            switch (timeUnit)
            {
                case SECONDS:
                    result = result.plusSeconds(sliceSize);
                    break;
                case MINUTES:
                    result = result.plusMinutes(sliceSize);
                    break;
                case HOURS:
                    result = result.plusHours(sliceSize);
                    break;
                case DAYS:
                    result = result.plusDays(sliceSize);
                    break;
                case WEEKS:
                    result = result.plusWeeks(sliceSize);
                    break;
                case MONTHS:
                    result = result.plusMonths(sliceSize);
                    break;
                case QUARTERS:
                    result = result.plusMonths(sliceSize * 3);
                    break;
                case YEARS:
                    result = result.plusYears(sliceSize);
                    break;
            }
        }
        
        return result;
    }
    
    private ZonedDateTime truncateToSecond(ZonedDateTime timestamp, int sliceSize)
    {
        long seconds = timestamp.getSecond();
        long truncatedSeconds = (seconds / sliceSize) * sliceSize;
        return timestamp.withSecond((int)truncatedSeconds).truncatedTo(ChronoUnit.SECONDS);
    }
    
    private ZonedDateTime truncateToMinute(ZonedDateTime timestamp, int sliceSize)
    {
        long minutes = timestamp.getMinute();
        long truncatedMinutes = (minutes / sliceSize) * sliceSize;
        return timestamp.withMinute((int)truncatedMinutes).truncatedTo(ChronoUnit.MINUTES);
    }
    
    private ZonedDateTime truncateToHour(ZonedDateTime timestamp, int sliceSize)
    {
        long hours = timestamp.getHour();
        long truncatedHours = (hours / sliceSize) * sliceSize;
        return timestamp.withHour((int)truncatedHours).truncatedTo(ChronoUnit.HOURS);
    }
    
    private ZonedDateTime truncateToDay(ZonedDateTime timestamp)
    {
        return timestamp.truncatedTo(ChronoUnit.DAYS);
    }
    
    private ZonedDateTime truncateToWeek(ZonedDateTime timestamp)
    {
        // Get the day of week (1-7, where 1 is Monday)
        int dayOfWeek = timestamp.getDayOfWeek().getValue();
        // Subtract days to get to the start of the week (Monday)
        return timestamp.minusDays(dayOfWeek - 1).truncatedTo(ChronoUnit.DAYS);
    }
    
    private ZonedDateTime truncateToMonth(ZonedDateTime timestamp)
    {
        return timestamp.withDayOfMonth(1).truncatedTo(ChronoUnit.DAYS);
    }
    
    private ZonedDateTime truncateToQuarter(ZonedDateTime timestamp)
    {
        int month = timestamp.getMonthValue();
        int quarterStartMonth = ((month - 1) / 3) * 3 + 1;
        return timestamp.withMonth(quarterStartMonth).withDayOfMonth(1).truncatedTo(ChronoUnit.DAYS);
    }
    
    private ZonedDateTime truncateToYear(ZonedDateTime timestamp)
    {
        return timestamp.withMonth(1).withDayOfMonth(1).truncatedTo(ChronoUnit.DAYS);
    }
}

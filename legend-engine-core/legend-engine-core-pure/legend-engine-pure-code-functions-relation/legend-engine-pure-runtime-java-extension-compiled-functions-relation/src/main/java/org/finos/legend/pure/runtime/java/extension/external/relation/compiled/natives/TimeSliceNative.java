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

package org.finos.legend.pure.runtime.java.extension.external.relation.compiled.natives;

import org.eclipse.collections.api.list.ListIterable;
import org.finos.legend.pure.m4.coreinstance.CoreInstance;
import org.finos.legend.pure.runtime.java.compiled.generation.ProcessorContext;
import org.finos.legend.pure.runtime.java.compiled.generation.processors.natives.AbstractNative;
import org.finos.legend.pure.runtime.java.compiled.generation.processors.natives.Native;

public class TimeSliceNative extends AbstractNative implements Native
{
    private final String functionSignature;

    public TimeSliceNative(String functionSignature)
    {
        super(functionSignature);
        this.functionSignature = functionSignature;
    }

    @Override
    public String build(CoreInstance topLevelElement, CoreInstance functionExpression, ListIterable<String> transformedParams, ProcessorContext processorContext)
    {
        StringBuilder builder = new StringBuilder();
        builder.append("org.finos.legend.pure.runtime.java.extension.external.relation.compiled.natives.TimeSlice.timeSlice(");
        
        // First parameter is the timestamp
        builder.append(transformedParams.get(0));
        
        // Second parameter is the timeUnit as a string
        builder.append(", ");
        builder.append(transformedParams.get(1));
        
        // Add additional parameters if they exist
        if (transformedParams.size() > 2)
        {
            builder.append(", ");
            builder.append(transformedParams.get(2));
            
            if (transformedParams.size() > 3)
            {
                builder.append(", ");
                builder.append(transformedParams.get(3));
            }
        }
        
        builder.append(")");
        return builder.toString();
    }
}

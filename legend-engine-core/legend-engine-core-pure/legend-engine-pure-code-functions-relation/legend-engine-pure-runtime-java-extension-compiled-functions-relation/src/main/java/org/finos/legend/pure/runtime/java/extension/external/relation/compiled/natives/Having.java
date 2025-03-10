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
import org.finos.legend.pure.m3.coreinstance.meta.pure.metamodel.function.LambdaFunction;
import org.finos.legend.pure.m3.execution.ExecutionSupport;
import org.finos.legend.pure.m4.coreinstance.CoreInstance;
import org.finos.legend.pure.runtime.java.compiled.execution.CompiledExecutionSupport;
import org.finos.legend.pure.runtime.java.compiled.generation.processors.natives.AbstractNative;
import org.finos.legend.pure.runtime.java.compiled.generation.processors.support.CompiledSupport;
import org.finos.legend.pure.runtime.java.extension.external.relation.compiled.RelationNativeImplementation;
import org.finos.legend.pure.runtime.java.extension.external.shared.conversion.Conversion;

import java.util.Stack;

public class Having extends AbstractNative
{
    public Having()
    {
        super("having_Relation_1__Function_1__Relation_1_");
    }

    @Override
    public String build(CoreInstance topLevelElement, CoreInstance functionExpression, ListIterable<String> transformedParams, ProcessorContext processorContext)
    {
        return "org.finos.legend.pure.runtime.java.extension.external.relation.compiled.RelationNativeImplementation.having(" + transformedParams.get(0) + ", " +
                Conversion.convertFunctionToFunction2(transformedParams.get(1), true) + ", es)";
    }

    @Override
    public String buildBody()
    {
        return "new DefendedPureFunction2<Object, Object, Object>()\n" +
                "        {\n" +
                "            @Override\n" +
                "            public Object value(Object relation, Object condition, ExecutionSupport es)\n" +
                "            {\n" +
                "                return org.finos.legend.pure.runtime.java.extension.external.relation.compiled.RelationNativeImplementation.having(relation, (org.finos.legend.pure.m3.execution.FunctionExecution.Function2<Object, ExecutionSupport, Boolean>)condition, es);\n" +
                "            }\n" +
                "        }";
    }
}

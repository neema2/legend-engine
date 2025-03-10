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
import org.eclipse.collections.api.list.MutableList;
import org.eclipse.collections.api.set.MutableIntSet;
import org.eclipse.collections.impl.factory.Lists;
import org.eclipse.collections.impl.set.mutable.primitive.IntHashSet;
import org.finos.legend.pure.m3.compiler.Context;
import org.finos.legend.pure.m3.coreinstance.meta.pure.metamodel.function.LambdaFunction;
import org.finos.legend.pure.m3.exception.PureExecutionException;
import org.finos.legend.pure.m3.navigation.Instance;
import org.finos.legend.pure.m3.navigation.M3Paths;
import org.finos.legend.pure.m3.navigation.M3Properties;
import org.finos.legend.pure.m3.navigation.ProcessorSupport;
import org.finos.legend.pure.m4.ModelRepository;
import org.finos.legend.pure.m4.coreinstance.CoreInstance;
import org.finos.legend.pure.runtime.java.extension.external.relation.interpreted.natives.shared.TestTDS;
import org.finos.legend.pure.runtime.java.extension.external.relation.interpreted.natives.shared.TestTDSContainer;
import org.finos.legend.pure.runtime.java.extension.external.shared.conversion.ConversionContext;
import org.finos.legend.pure.runtime.java.extension.external.shared.conversion.Conversions;
import org.finos.legend.pure.runtime.java.interpreted.ExecutionSupport;
import org.finos.legend.pure.runtime.java.interpreted.FunctionExecutionInterpreted;
import org.finos.legend.pure.runtime.java.interpreted.VariableContext;
import org.finos.legend.pure.runtime.java.interpreted.natives.InstantiationContext;
import org.finos.legend.pure.runtime.java.interpreted.natives.NativeFunction;
import org.finos.legend.pure.runtime.java.interpreted.profiler.Profiler;

import java.util.Stack;

public class Having implements NativeFunction
{
    private final ModelRepository repository;

    public Having(ModelRepository repository)
    {
        this.repository = repository;
    }

    @Override
    public CoreInstance execute(ListIterable<? extends CoreInstance> params, Stack<MutableList<CoreInstance>> resolvedTypeParameters, Stack<MutableList<CoreInstance>> resolvedMultiplicityParameters, VariableContext variableContext, CoreInstance functionExpressionToUseInStack, Profiler profiler, InstantiationContext instantiationContext, ExecutionSupport executionSupport, Context context, ProcessorSupport processorSupport) throws PureExecutionException
    {
        CoreInstance relation = params.get(0);
        CoreInstance function = params.get(1);

        if (!(relation instanceof TestTDSContainer))
        {
            throw new PureExecutionException(functionExpressionToUseInStack.getSourceInformation(), "Expected a relation, found: " + Instance.getValueForMetaPropertyToOneResolved(relation, M3Properties.classifierGenericType, processorSupport).getName());
        }

        TestTDS tds = ((TestTDSContainer) relation).getTds();
        MutableIntSet list = new IntHashSet();
        LambdaFunction<?> lambdaFunction = (LambdaFunction<?>) function;
        CoreInstance functionType = Instance.getValueForMetaPropertyToOneResolved(lambdaFunction, M3Properties.classifierGenericType, processorSupport);
        ListIterable<? extends CoreInstance> typeArguments = Instance.getValueForMetaPropertyToManyResolved(functionType, M3Properties.typeArguments, processorSupport);
        CoreInstance functionReturnType = typeArguments.get(1);
        boolean isBoolean = Instance.instanceOf(functionReturnType, M3Paths.Boolean, processorSupport);
        if (!isBoolean)
        {
            throw new PureExecutionException(functionExpressionToUseInStack.getSourceInformation(), "Expected a function that returns Boolean, found: " + functionReturnType.getName());
        }

        for (int i = 0; i < tds.getRowCount(); i++)
        {
            CoreInstance row = tds.getRow(i);
            MutableList<CoreInstance> args = Lists.mutable.with(row);
            CoreInstance result = FunctionExecutionInterpreted.executeFunction(false, lambdaFunction, args, resolvedTypeParameters, resolvedMultiplicityParameters, variableContext, functionExpressionToUseInStack, profiler, instantiationContext, executionSupport, Conversions.fromPureCollection(Lists.mutable.empty(), ConversionContext.build(processorSupport, repository)), processorSupport);
            if (!Instance.getValueForMetaPropertyToOneResolved(result, M3Properties.values, processorSupport).getName().equals("true"))
            {
                list.add(i);
            }
        }
        return new TestTDSContainer(tds.drop(list));
    }
}

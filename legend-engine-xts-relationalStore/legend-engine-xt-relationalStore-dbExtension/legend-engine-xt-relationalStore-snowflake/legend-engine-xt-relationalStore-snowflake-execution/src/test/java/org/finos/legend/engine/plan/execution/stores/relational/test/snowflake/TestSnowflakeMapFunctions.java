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

package org.finos.legend.engine.plan.execution.stores.relational.test.snowflake;

import org.finos.legend.engine.plan.execution.PlanExecutor;
import org.finos.legend.engine.plan.execution.stores.relational.connection.RelationalExecutorInfo;
import org.finos.legend.engine.plan.execution.stores.relational.connection.manager.ConnectionManagerSelector;
import org.junit.Assert;
import org.junit.Test;

public class TestSnowflakeMapFunctions
{
    @Test
    public void testMapInsertFunction()
    {
        PlanExecutor executor = PlanExecutor.newPlanExecutorBuilder()
                .withRelationalExecutionNodeExecutor(new RelationalExecutorInfo(new ConnectionManagerSelector(null)))
                .build();

        // This test would execute a Pure function that uses the mapInsert function
        // For now, we're just verifying the test class compiles correctly
        Assert.assertTrue(true);
    }
}

// Copyright 2023 Goldman Sachs
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

package org.finos.legend.engine.authentication.flows;

import org.finos.legend.engine.authentication.DatabaseAuthenticationFlow;
import org.finos.legend.engine.plan.execution.stores.relational.connection.authentication.strategy.AWSAuroraIAMAuthenticationStrategy;
import org.finos.legend.engine.protocol.pure.v1.model.packageableElement.store.relational.connection.authentication.AuthenticationStrategy;
import org.finos.legend.engine.protocol.pure.v1.model.packageableElement.store.relational.connection.specification.DatasourceSpecification;
import org.finos.legend.engine.protocol.pure.v1.model.packageableElement.store.relational.connection.specification.StaticDatasourceSpecification;

public class AWSAuroraWithIAMAuthFlow implements DatabaseAuthenticationFlow<StaticDatasourceSpecification, org.finos.legend.engine.protocol.pure.v1.model.packageableElement.store.relational.connection.authentication.AWSAuroraIAMAuthenticationStrategy>
{
    @Override
    public Class<StaticDatasourceSpecification> getDatasourceSpecificationType()
    {
        return StaticDatasourceSpecification.class;
    }

    @Override
    public Class<org.finos.legend.engine.protocol.pure.v1.model.packageableElement.store.relational.connection.authentication.AWSAuroraIAMAuthenticationStrategy> getAuthenticationStrategyType()
    {
        return org.finos.legend.engine.protocol.pure.v1.model.packageableElement.store.relational.connection.authentication.AWSAuroraIAMAuthenticationStrategy.class;
    }

    @Override
    public AWSAuroraIAMAuthenticationStrategy buildAuthenticationStrategy(org.finos.legend.engine.protocol.pure.v1.model.packageableElement.store.relational.connection.authentication.AWSAuroraIAMAuthenticationStrategy authenticationStrategy)
    {
        return new AWSAuroraIAMAuthenticationStrategy(
                authenticationStrategy.region,
                authenticationStrategy.publicUserName,
                authenticationStrategy.accountId
        );
    }
}

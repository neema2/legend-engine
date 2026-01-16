// Copyright 2025 Goldman Sachs
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

package org.finos.legend.engine.language.pure.compiler.toPureGraph;

import org.eclipse.collections.api.block.function.Function2;
import org.eclipse.collections.api.factory.Lists;
import org.eclipse.collections.api.list.MutableList;
import org.finos.legend.engine.language.pure.compiler.toPureGraph.extension.CompilerExtension;
import org.finos.legend.engine.protocol.pure.v1.model.packageableElement.store.relational.connection.DatabaseType;
import org.finos.legend.engine.protocol.pure.v1.model.packageableElement.store.relational.connection.authentication.AWSIAMDatabaseAuthenticationStrategy;
import org.finos.legend.engine.protocol.pure.v1.model.packageableElement.store.relational.connection.authentication.AuthenticationStrategy;
import org.finos.legend.engine.protocol.pure.v1.model.packageableElement.store.relational.connection.flows.DatabaseAuthenticationFlowKey;
import org.finos.legend.engine.protocol.pure.v1.model.packageableElement.store.relational.connection.specification.AuroraPostgresDatasourceSpecification;
import org.finos.legend.engine.protocol.pure.v1.model.packageableElement.store.relational.connection.specification.DatasourceSpecification;
import org.finos.legend.pure.generated.Root_meta_pure_alloy_connections_alloy_authentication_AuthenticationStrategy;
import org.finos.legend.pure.generated.Root_meta_pure_alloy_connections_alloy_specification_DatasourceSpecification;
import org.finos.legend.pure.generated.Root_meta_pure_legend_connections_legend_specification_AuroraPostgresDatasourceSpecification;
import org.finos.legend.pure.generated.Root_meta_pure_legend_connections_legend_specification_AuroraPostgresDatasourceSpecification_Impl;
import org.finos.legend.pure.generated.Root_meta_pure_legend_connections_legend_authentication_AWSIAMDatabaseAuthenticationStrategy;
import org.finos.legend.pure.generated.Root_meta_pure_legend_connections_legend_authentication_AWSIAMDatabaseAuthenticationStrategy_Impl;

import java.util.List;

public class AuroraPostgresCompilerExtension implements IRelationalCompilerExtension
{
    @Override
    public MutableList<String> group()
    {
        return Lists.mutable.with("Store", "Relational", "AuroraPostgres");
    }

    @Override
    public CompilerExtension build()
    {
        return new AuroraPostgresCompilerExtension();
    }

    @Override
    public List<Function2<DatasourceSpecification, CompileContext, Root_meta_pure_alloy_connections_alloy_specification_DatasourceSpecification>> getExtraDataSourceSpecificationProcessors()
    {
        return Lists.mutable.with((datasourceSpecification, context) ->
        {
            if (datasourceSpecification instanceof AuroraPostgresDatasourceSpecification)
            {
                AuroraPostgresDatasourceSpecification spec = (AuroraPostgresDatasourceSpecification) datasourceSpecification;
                Root_meta_pure_legend_connections_legend_specification_AuroraPostgresDatasourceSpecification pureSpec = 
                        new Root_meta_pure_legend_connections_legend_specification_AuroraPostgresDatasourceSpecification_Impl(
                                "", 
                                null, 
                                context.pureModel.getClass("meta::pure::legend::connections::legend::specification::AuroraPostgresDatasourceSpecification")
                        );
                pureSpec._host(spec.host);
                pureSpec._port(spec.port);
                pureSpec._databaseName(spec.databaseName);
                pureSpec._region(spec.region);
                if (spec.clusterIdentifier != null)
                {
                    pureSpec._clusterIdentifier(spec.clusterIdentifier);
                }
                return pureSpec;
            }
            return null;
        });
    }

    @Override
    public List<Function2<AuthenticationStrategy, CompileContext, Root_meta_pure_alloy_connections_alloy_authentication_AuthenticationStrategy>> getExtraAuthenticationStrategyProcessors()
    {
        return Lists.mutable.with((authenticationStrategy, context) ->
        {
            if (authenticationStrategy instanceof AWSIAMDatabaseAuthenticationStrategy)
            {
                AWSIAMDatabaseAuthenticationStrategy strategy = (AWSIAMDatabaseAuthenticationStrategy) authenticationStrategy;
                Root_meta_pure_legend_connections_legend_authentication_AWSIAMDatabaseAuthenticationStrategy pureStrategy = 
                        new Root_meta_pure_legend_connections_legend_authentication_AWSIAMDatabaseAuthenticationStrategy_Impl(
                                "", 
                                null, 
                                context.pureModel.getClass("meta::pure::legend::connections::legend::authentication::AWSIAMDatabaseAuthenticationStrategy")
                        );
                pureStrategy._databaseUsername(strategy.databaseUsername);
                // AWS credentials would need to be compiled as well - simplified for now
                return pureStrategy;
            }
            return null;
        });
    }

    @Override
    public List<DatabaseAuthenticationFlowKey> getFlowKeys()
    {
        return Lists.mutable.of(
                DatabaseAuthenticationFlowKey.newKey(
                        DatabaseType.Postgres,
                        AuroraPostgresDatasourceSpecification.class,
                        AWSIAMDatabaseAuthenticationStrategy.class
                )
        );
    }
}

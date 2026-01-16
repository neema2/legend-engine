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

package org.finos.legend.engine.plan.execution.stores.relational;

import org.eclipse.collections.api.block.function.Function2;
import org.eclipse.collections.api.factory.Lists;
import org.eclipse.collections.api.list.MutableList;
import org.finos.legend.engine.plan.execution.stores.relational.connection.ConnectionExtension;
import org.finos.legend.engine.plan.execution.stores.relational.connection.ConnectionKey;
import org.finos.legend.engine.plan.execution.stores.relational.connection.authentication.AuthenticationStrategy;
import org.finos.legend.engine.plan.execution.stores.relational.connection.authentication.strategy.OAuthProfile;
import org.finos.legend.engine.plan.execution.stores.relational.connection.authentication.strategy.keys.AuthenticationStrategyKey;
import org.finos.legend.engine.plan.execution.stores.relational.connection.driver.DatabaseManager;
import org.finos.legend.engine.plan.execution.stores.relational.connection.driver.vendors.aurorapostgres.AuroraPostgresManager;
import org.finos.legend.engine.plan.execution.stores.relational.connection.ds.DataSourceSpecification;
import org.finos.legend.engine.plan.execution.stores.relational.connection.ds.DataSourceSpecificationKey;
import org.finos.legend.engine.plan.execution.stores.relational.connection.ds.specifications.AuroraPostgresDataSourceSpecification;
import org.finos.legend.engine.plan.execution.stores.relational.connection.ds.specifications.keys.AuroraPostgresDataSourceSpecificationKey;
import org.finos.legend.engine.plan.execution.stores.relational.connection.manager.strategic.StrategicConnectionExtension;
import org.finos.legend.engine.protocol.pure.v1.model.packageableElement.store.relational.connection.RelationalDatabaseConnection;
import org.finos.legend.engine.protocol.pure.v1.model.packageableElement.store.relational.connection.authentication.AWSIAMDatabaseAuthenticationStrategy;
import org.finos.legend.engine.protocol.pure.v1.model.packageableElement.store.relational.connection.authentication.AuthenticationStrategyVisitor;
import org.finos.legend.engine.protocol.pure.v1.model.packageableElement.store.relational.connection.specification.AuroraPostgresDatasourceSpecification;
import org.finos.legend.engine.protocol.pure.v1.model.packageableElement.store.relational.connection.specification.DatasourceSpecificationVisitor;

import java.util.List;
import java.util.function.Function;

/**
 * Connection extension for Aurora PostgreSQL databases.
 * 
 * Provides the necessary components for Legend to connect to Aurora PostgreSQL
 * databases using IAM authentication.
 */
public class AuroraPostgresConnectionExtension implements ConnectionExtension, StrategicConnectionExtension
{
    @Override
    public String type()
    {
        return "AuroraPostgres_ConnectionExtension";
    }

    @Override
    public MutableList<String> group()
    {
        return Lists.mutable.with("Store", "Relational", "AuroraPostgres");
    }

    @Override
    public MutableList<DatabaseManager> getAdditionalDatabaseManager()
    {
        return Lists.mutable.of(new AuroraPostgresManager());
    }

    @Override
    public AuthenticationStrategyVisitor<AuthenticationStrategyKey> getExtraAuthenticationKeyGenerators()
    {
        return authenticationStrategy ->
        {
            if (authenticationStrategy instanceof AWSIAMDatabaseAuthenticationStrategy)
            {
                AWSIAMDatabaseAuthenticationStrategy strategy = (AWSIAMDatabaseAuthenticationStrategy) authenticationStrategy;
                return new AWSIAMDatabaseAuthenticationStrategyKey(strategy.databaseUsername);
            }
            return null;
        };
    }

    @Override
    public AuthenticationStrategyVisitor<AuthenticationStrategy> getExtraAuthenticationStrategyTransformGenerators(List<OAuthProfile> oauthProfiles)
    {
        return authenticationStrategy ->
        {
            if (authenticationStrategy instanceof AWSIAMDatabaseAuthenticationStrategy)
            {
                AWSIAMDatabaseAuthenticationStrategy strategy = (AWSIAMDatabaseAuthenticationStrategy) authenticationStrategy;
                return new org.finos.legend.engine.plan.execution.stores.relational.connection.authentication.strategy.AWSIAMDatabaseAuthenticationStrategy(
                        strategy.databaseUsername,
                        strategy.awsCredentials
                );
            }
            return null;
        };
    }

    @Override
    public Function<RelationalDatabaseConnection, DatasourceSpecificationVisitor<DataSourceSpecificationKey>> getExtraDataSourceSpecificationKeyGenerators(int testDbPort)
    {
        return connection -> datasourceSpecification ->
        {
            if (datasourceSpecification instanceof AuroraPostgresDatasourceSpecification)
            {
                AuroraPostgresDatasourceSpecification spec = (AuroraPostgresDatasourceSpecification) datasourceSpecification;
                return new AuroraPostgresDataSourceSpecificationKey(
                        spec.host,
                        spec.port,
                        spec.databaseName,
                        spec.region,
                        spec.clusterIdentifier
                );
            }
            return null;
        };
    }

    @Override
    public Function2<RelationalDatabaseConnection, ConnectionKey, DatasourceSpecificationVisitor<DataSourceSpecification>> getExtraDataSourceSpecificationTransformerGenerators(Function<RelationalDatabaseConnection, AuthenticationStrategy> authenticationStrategyProvider)
    {
        return (connection, connectionKey) -> datasourceSpecification ->
        {
            if (datasourceSpecification instanceof AuroraPostgresDatasourceSpecification)
            {
                return new AuroraPostgresDataSourceSpecification(
                        (AuroraPostgresDataSourceSpecificationKey) connectionKey.getDataSourceSpecificationKey(),
                        new AuroraPostgresManager(),
                        authenticationStrategyProvider.apply(connection)
                );
            }
            return null;
        };
    }
}

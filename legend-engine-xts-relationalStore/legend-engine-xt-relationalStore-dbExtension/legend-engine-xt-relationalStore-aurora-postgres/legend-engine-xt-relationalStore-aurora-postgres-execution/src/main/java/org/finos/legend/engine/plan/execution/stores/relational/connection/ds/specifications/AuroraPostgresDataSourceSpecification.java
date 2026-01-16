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

package org.finos.legend.engine.plan.execution.stores.relational.connection.ds.specifications;

import org.finos.legend.engine.plan.execution.stores.relational.connection.authentication.AuthenticationStrategy;
import org.finos.legend.engine.plan.execution.stores.relational.connection.driver.DatabaseManager;
import org.finos.legend.engine.plan.execution.stores.relational.connection.driver.vendors.aurorapostgres.AuroraPostgresManager;
import org.finos.legend.engine.plan.execution.stores.relational.connection.ds.DataSourceSpecification;
import org.finos.legend.engine.plan.execution.stores.relational.connection.ds.specifications.keys.AuroraPostgresDataSourceSpecificationKey;

import java.util.Properties;

/**
 * Data source specification for Aurora PostgreSQL connections.
 */
public class AuroraPostgresDataSourceSpecification extends DataSourceSpecification
{
    public AuroraPostgresDataSourceSpecification(
            AuroraPostgresDataSourceSpecificationKey key,
            DatabaseManager databaseManager,
            AuthenticationStrategy authenticationStrategy)
    {
        this(key, databaseManager, authenticationStrategy, createProperties(key));
    }

    private AuroraPostgresDataSourceSpecification(
            AuroraPostgresDataSourceSpecificationKey key,
            DatabaseManager databaseManager,
            AuthenticationStrategy authenticationStrategy,
            Properties extraUserProperties)
    {
        super(key, databaseManager, authenticationStrategy, extraUserProperties);
    }

    private static Properties createProperties(AuroraPostgresDataSourceSpecificationKey key)
    {
        Properties props = new Properties();
        props.put(AuroraPostgresManager.AURORA_REGION, key.getRegion());
        if (key.getClusterIdentifier() != null)
        {
            props.put(AuroraPostgresManager.AURORA_CLUSTER_ID, key.getClusterIdentifier());
        }
        return props;
    }

    @Override
    protected String getJdbcUrl(String host, int port, String databaseName, Properties properties)
    {
        AuroraPostgresDataSourceSpecificationKey key = (AuroraPostgresDataSourceSpecificationKey) this.datasourceKey;
        return super.getJdbcUrl(key.getHost(), key.getPort(), key.getDatabaseName(), properties);
    }
}

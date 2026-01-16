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

package org.finos.legend.engine.plan.execution.stores.relational.connection.driver.vendors.aurorapostgres;

import org.eclipse.collections.api.list.MutableList;
import org.eclipse.collections.impl.factory.Lists;
import org.finos.legend.engine.plan.execution.stores.relational.connection.authentication.AuthenticationStrategy;
import org.finos.legend.engine.plan.execution.stores.relational.connection.driver.DatabaseManager;
import org.finos.legend.engine.plan.execution.stores.relational.connection.driver.commands.RelationalDatabaseCommands;

import java.util.Properties;

/**
 * Database manager for AWS Aurora PostgreSQL.
 * 
 * Aurora PostgreSQL uses the standard PostgreSQL JDBC driver but requires
 * SSL for IAM authentication. The connection URL format is the same as
 * PostgreSQL with SSL parameters enabled.
 */
public class AuroraPostgresManager extends DatabaseManager
{
    public static final String AURORA_REGION = "auroraRegion";
    public static final String AURORA_CLUSTER_ID = "auroraClusterIdentifier";

    @Override
    public MutableList<String> getIds()
    {
        return Lists.mutable.with("AuroraPostgres");
    }

    @Override
    public String buildURL(String host, int port, String databaseName, Properties extraUserDataSourceProperties, AuthenticationStrategy authenticationStrategy)
    {
        // Aurora PostgreSQL requires SSL for IAM authentication
        // sslmode=require ensures encrypted connection
        // sslrootcert can be used to specify the RDS CA certificate
        return "jdbc:postgresql://" + host + ":" + port + "/" + databaseName + 
               "?ssl=true&sslmode=require";
    }

    @Override
    public String getDriver()
    {
        return "org.finos.legend.engine.plan.execution.stores.relational.connection.driver.vendors.aurorapostgres.AuroraPostgresDriver";
    }

    @Override
    public RelationalDatabaseCommands relationalDatabaseSupport()
    {
        return new AuroraPostgresCommands();
    }
}

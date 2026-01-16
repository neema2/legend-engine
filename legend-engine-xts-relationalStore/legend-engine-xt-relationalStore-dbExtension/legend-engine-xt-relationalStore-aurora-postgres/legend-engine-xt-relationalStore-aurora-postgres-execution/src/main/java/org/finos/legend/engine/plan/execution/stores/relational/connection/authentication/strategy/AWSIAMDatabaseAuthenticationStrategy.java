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

package org.finos.legend.engine.plan.execution.stores.relational.connection.authentication.strategy;

import org.eclipse.collections.api.tuple.Pair;
import org.eclipse.collections.impl.tuple.Tuples;
import org.finos.legend.engine.plan.execution.stores.relational.AWSIAMDatabaseAuthenticationStrategyKey;
import org.finos.legend.engine.plan.execution.stores.relational.connection.ConnectionException;
import org.finos.legend.engine.plan.execution.stores.relational.connection.authentication.AuthenticationStrategy;
import org.finos.legend.engine.plan.execution.stores.relational.connection.authentication.strategy.keys.AuthenticationStrategyKey;
import org.finos.legend.engine.plan.execution.stores.relational.connection.ds.DataSourceWithStatistics;
import org.finos.legend.engine.plan.execution.stores.relational.connection.driver.DatabaseManager;
import org.finos.legend.engine.plan.execution.stores.relational.connection.driver.vendors.aurorapostgres.AuroraPostgresManager;
import org.finos.legend.engine.protocol.pure.v1.model.packageableElement.authentication.vault.aws.AWSCredentials;
import org.finos.legend.engine.shared.core.identity.Identity;
import org.finos.legend.engine.shared.core.identity.credential.PlaintextUserPasswordCredential;
import software.amazon.awssdk.auth.credentials.AwsCredentialsProvider;
import software.amazon.awssdk.auth.credentials.DefaultCredentialsProvider;
import software.amazon.awssdk.regions.Region;
import software.amazon.awssdk.services.rds.RdsUtilities;

import java.sql.Connection;
import java.sql.SQLException;
import java.util.Properties;

/**
 * Runtime authentication strategy for AWS IAM Database Authentication.
 * 
 * This strategy generates IAM authentication tokens at connection time
 * and uses them as passwords for database connections.
 */
public class AWSIAMDatabaseAuthenticationStrategy extends AuthenticationStrategy
{
    private final String databaseUsername;
    private final AWSCredentials awsCredentials;

    public AWSIAMDatabaseAuthenticationStrategy(String databaseUsername, AWSCredentials awsCredentials)
    {
        this.databaseUsername = databaseUsername;
        this.awsCredentials = awsCredentials;
    }

    @Override
    public Connection getConnectionImpl(DataSourceWithStatistics ds, Identity identity) throws ConnectionException
    {
        try
        {
            return ds.getDataSource().getConnection();
        }
        catch (SQLException e)
        {
            throw new ConnectionException(e);
        }
    }

    @Override
    public Pair<String, Properties> handleConnection(String url, Properties properties, DatabaseManager databaseManager)
    {
        Properties connectionProperties = new Properties();
        connectionProperties.putAll(properties);

        // Get the region from datasource properties
        String region = properties.getProperty(AuroraPostgresManager.AURORA_REGION, "us-east-1");

        // Extract host and port from URL
        // URL format: jdbc:postgresql://host:port/database?params
        String host = extractHostFromUrl(url);
        int port = extractPortFromUrl(url);

        // Generate the IAM authentication token
        AwsCredentialsProvider credentialsProvider = resolveCredentials();
        
        RdsUtilities rdsUtilities = RdsUtilities.builder()
                .region(Region.of(region))
                .credentialsProvider(credentialsProvider)
                .build();

        String authToken = rdsUtilities.generateAuthenticationToken(builder -> builder
                .hostname(host)
                .port(port)
                .username(databaseUsername)
        );

        connectionProperties.put("user", databaseUsername);
        connectionProperties.put("password", authToken);

        return Tuples.pair(url, connectionProperties);
    }

    @Override
    public AuthenticationStrategyKey getKey()
    {
        return new AWSIAMDatabaseAuthenticationStrategyKey(databaseUsername);
    }

    private AwsCredentialsProvider resolveCredentials()
    {
        // For now, use default credentials provider
        // The full implementation would handle all AWS credential types
        return DefaultCredentialsProvider.create();
    }

    private String extractHostFromUrl(String url)
    {
        // jdbc:postgresql://host:port/database
        String withoutPrefix = url.replace("jdbc:postgresql://", "");
        int colonIndex = withoutPrefix.indexOf(':');
        if (colonIndex > 0)
        {
            return withoutPrefix.substring(0, colonIndex);
        }
        int slashIndex = withoutPrefix.indexOf('/');
        if (slashIndex > 0)
        {
            return withoutPrefix.substring(0, slashIndex);
        }
        return withoutPrefix;
    }

    private int extractPortFromUrl(String url)
    {
        // jdbc:postgresql://host:port/database
        String withoutPrefix = url.replace("jdbc:postgresql://", "");
        int colonIndex = withoutPrefix.indexOf(':');
        if (colonIndex > 0)
        {
            int slashIndex = withoutPrefix.indexOf('/');
            String portStr = withoutPrefix.substring(colonIndex + 1, slashIndex > colonIndex ? slashIndex : withoutPrefix.length());
            // Handle query parameters
            int questionIndex = portStr.indexOf('?');
            if (questionIndex > 0)
            {
                portStr = portStr.substring(0, questionIndex);
            }
            try
            {
                return Integer.parseInt(portStr);
            }
            catch (NumberFormatException e)
            {
                return 5432; // Default PostgreSQL port
            }
        }
        return 5432;
    }
}

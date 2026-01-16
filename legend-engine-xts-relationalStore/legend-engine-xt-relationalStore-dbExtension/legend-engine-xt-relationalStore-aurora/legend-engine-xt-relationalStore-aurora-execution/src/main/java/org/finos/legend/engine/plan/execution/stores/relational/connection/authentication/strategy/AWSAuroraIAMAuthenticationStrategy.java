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

package org.finos.legend.engine.plan.execution.stores.relational.connection.authentication.strategy;

import org.eclipse.collections.api.tuple.Pair;
import org.eclipse.collections.impl.tuple.Tuples;
import org.finos.legend.engine.plan.execution.stores.relational.connection.ConnectionException;
import org.finos.legend.engine.plan.execution.stores.relational.connection.authentication.AuthenticationStrategy;
import org.finos.legend.engine.plan.execution.stores.relational.connection.authentication.strategy.keys.AuthenticationStrategyKey;
import org.finos.legend.engine.plan.execution.stores.relational.connection.driver.DatabaseManager;
import org.finos.legend.engine.plan.execution.stores.relational.connection.ds.DataSourceWithStatistics;
import org.finos.legend.engine.shared.core.identity.Identity;
import software.amazon.awssdk.auth.credentials.DefaultCredentialsProvider;
import software.amazon.awssdk.regions.Region;
import software.amazon.awssdk.services.rds.RdsUtilities;

import java.sql.Connection;
import java.sql.SQLException;
import java.util.Properties;

public class AWSAuroraIAMAuthenticationStrategy extends AuthenticationStrategy
{
    private final String region;
    private final String publicUserName;
    private final String accountId;

    public AWSAuroraIAMAuthenticationStrategy(String region, String publicUserName, String accountId)
    {
        this.region = region;
        this.publicUserName = publicUserName;
        this.accountId = accountId;
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
        
        String host = properties.getProperty("host");
        String portStr = properties.getProperty("port");
        
        // If host/port are not in properties, we might need to parse them from URL, but usually they are passed in properties by the DataSourceSpecification
        if (host == null || portStr == null)
        {
             // Fallback or error? For now assuming they are present or managed by driver config.
             // Actually, for JDBC, we often need to set the password to the token.
             // The URL parsing depends on the driver, but here we need it for token generation.
             // Let's assume standard properties or try to extract from url if missing.
        }

        int port = portStr != null ? Integer.parseInt(portStr) : 5432; // Default postgres/aurora port?

        String token = generateAuthToken(host, port, this.publicUserName, this.region);
        
        connectionProperties.put("user", this.publicUserName);
        connectionProperties.put("password", token);

        return Tuples.pair(url, connectionProperties);
    }

    private String generateAuthToken(String host, int port, String userName, String regionName)
    {
        RdsUtilities utilities = RdsUtilities.builder()
                .region(Region.of(regionName))
                .build();

        return utilities.generateAuthenticationToken(builder -> builder
                .hostname(host)
                .port(port)
                .username(userName)
                .credentialProvider(DefaultCredentialsProvider.create())
                .region(Region.of(regionName))
        );
    }

    @Override
    public AuthenticationStrategyKey getKey()
    {
        // Simple key for now, might need a proper Key implementation if caching/hashing is strict
        return new AuthenticationStrategyKey()
        {
            @Override
            public String shortId()
            {
                return "awsAuroraIAM";
            }

            @Override
            public String id()
            {
                return "AWSAuroraIAMAuthenticationStrategy";
            }
        };
    }
}

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

package org.finos.legend.engine.plan.execution.stores.relational.connection.ds.specifications.keys;

import org.finos.legend.engine.plan.execution.stores.relational.connection.ds.DataSourceSpecificationKey;

import java.util.Objects;

/**
 * Key for identifying and caching Aurora PostgreSQL data source connections.
 */
public class AuroraPostgresDataSourceSpecificationKey implements DataSourceSpecificationKey
{
    private final String host;
    private final int port;
    private final String databaseName;
    private final String region;
    private final String clusterIdentifier;

    public AuroraPostgresDataSourceSpecificationKey(String host, int port, String databaseName, String region, String clusterIdentifier)
    {
        this.host = host;
        this.port = port;
        this.databaseName = databaseName;
        this.region = region;
        this.clusterIdentifier = clusterIdentifier;
    }

    public String getHost()
    {
        return host;
    }

    public int getPort()
    {
        return port;
    }

    public String getDatabaseName()
    {
        return databaseName;
    }

    public String getRegion()
    {
        return region;
    }

    public String getClusterIdentifier()
    {
        return clusterIdentifier;
    }

    @Override
    public String toString()
    {
        return "AuroraPostgresDataSourceSpecificationKey{" +
                "host='" + host + '\'' +
                ", port=" + port +
                ", databaseName='" + databaseName + '\'' +
                ", region='" + region + '\'' +
                ", clusterIdentifier='" + clusterIdentifier + '\'' +
                '}';
    }

    @Override
    public String shortId()
    {
        return "AuroraPostgres_" +
                "host:" + host + "_" +
                "port:" + port + "_" +
                "db:" + databaseName + "_" +
                "region:" + region;
    }

    @Override
    public boolean equals(Object o)
    {
        if (this == o) return true;
        if (o == null || getClass() != o.getClass()) return false;
        AuroraPostgresDataSourceSpecificationKey that = (AuroraPostgresDataSourceSpecificationKey) o;
        return port == that.port &&
                Objects.equals(host, that.host) &&
                Objects.equals(databaseName, that.databaseName) &&
                Objects.equals(region, that.region) &&
                Objects.equals(clusterIdentifier, that.clusterIdentifier);
    }

    @Override
    public int hashCode()
    {
        return Objects.hash(host, port, databaseName, region, clusterIdentifier);
    }
}

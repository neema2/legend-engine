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

package org.finos.legend.engine.protocol.pure.v1.model.packageableElement.store.relational.connection.specification;

/**
 * Datasource specification for AWS Aurora PostgreSQL databases.
 * Aurora PostgreSQL is wire-compatible with PostgreSQL but requires
 * Aurora-specific connection parameters for IAM authentication.
 */
public class AuroraPostgresDatasourceSpecification extends DatasourceSpecification
{
    /**
     * The Aurora cluster endpoint hostname.
     * Example: my-cluster.cluster-xxxxx.us-east-1.rds.amazonaws.com
     */
    public String host;

    /**
     * The database port (default: 5432 for PostgreSQL).
     */
    public int port;

    /**
     * The name of the database to connect to.
     */
    public String databaseName;

    /**
     * The AWS region where the Aurora cluster is located.
     * Required for IAM authentication token generation.
     * Example: us-east-1
     */
    public String region;

    /**
     * Optional Aurora cluster identifier.
     * Useful for reference and logging.
     */
    public String clusterIdentifier;

    @Override
    public <T> T accept(DatasourceSpecificationVisitor<T> datasourceSpecificationVisitor)
    {
        return datasourceSpecificationVisitor.visit(this);
    }
}

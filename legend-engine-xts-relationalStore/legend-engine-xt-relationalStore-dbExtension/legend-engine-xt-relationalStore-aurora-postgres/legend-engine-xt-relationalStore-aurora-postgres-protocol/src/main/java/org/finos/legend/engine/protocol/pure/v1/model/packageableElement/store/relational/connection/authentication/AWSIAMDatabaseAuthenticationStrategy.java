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

package org.finos.legend.engine.protocol.pure.v1.model.packageableElement.store.relational.connection.authentication;

import org.finos.legend.engine.protocol.pure.v1.model.packageableElement.authentication.vault.aws.AWSCredentials;

/**
 * Authentication strategy for AWS IAM Database Authentication.
 * 
 * This strategy uses AWS IAM credentials to generate short-lived authentication
 * tokens that are used as passwords when connecting to Aurora PostgreSQL databases.
 * 
 * Prerequisites:
 * - The Aurora cluster must have IAM database authentication enabled
 * - A database user must be created and granted the rds_iam role
 * - The IAM principal must have the rds-db:connect permission
 */
public class AWSIAMDatabaseAuthenticationStrategy extends AuthenticationStrategy
{
    /**
     * The database username that has been configured for IAM authentication.
     * This user must exist in the database and have the rds_iam role granted.
     * 
     * In PostgreSQL, this is created with:
     * CREATE USER iam_user WITH LOGIN;
     * GRANT rds_iam TO iam_user;
     */
    public String databaseUsername;

    /**
     * AWS credentials configuration for obtaining IAM authentication tokens.
     * Can be one of:
     * - AWSDefaultCredentials: Use default credential chain (environment, instance profile, etc.)
     * - AWSStaticCredentials: Use explicit access key and secret
     * - AWSSTSAssumeRoleCredentials: Assume an IAM role
     */
    public AWSCredentials awsCredentials;

    @Override
    public <T> T accept(AuthenticationStrategyVisitor<T> authenticationStrategyVisitor)
    {
        return authenticationStrategyVisitor.visit(this);
    }
}

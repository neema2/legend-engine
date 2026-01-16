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

package org.finos.legend.engine.authentication.flows;

import org.finos.legend.engine.authentication.DatabaseAuthenticationFlow;
import org.finos.legend.engine.protocol.pure.v1.model.packageableElement.authentication.vault.aws.AWSCredentials;
import org.finos.legend.engine.protocol.pure.v1.model.packageableElement.authentication.vault.aws.AWSDefaultCredentials;
import org.finos.legend.engine.protocol.pure.v1.model.packageableElement.authentication.vault.aws.AWSSTSAssumeRoleCredentials;
import org.finos.legend.engine.protocol.pure.v1.model.packageableElement.authentication.vault.aws.AWSStaticCredentials;
import org.finos.legend.engine.protocol.pure.v1.model.packageableElement.store.relational.connection.DatabaseType;
import org.finos.legend.engine.protocol.pure.v1.model.packageableElement.store.relational.connection.authentication.AWSIAMDatabaseAuthenticationStrategy;
import org.finos.legend.engine.protocol.pure.v1.model.packageableElement.store.relational.connection.specification.AuroraPostgresDatasourceSpecification;
import org.finos.legend.engine.shared.core.identity.Credential;
import org.finos.legend.engine.shared.core.identity.Identity;
import org.finos.legend.engine.shared.core.identity.credential.PlaintextUserPasswordCredential;
import org.finos.legend.engine.shared.core.vault.Vault;
import software.amazon.awssdk.auth.credentials.AwsBasicCredentials;
import software.amazon.awssdk.auth.credentials.AwsCredentialsProvider;
import software.amazon.awssdk.auth.credentials.DefaultCredentialsProvider;
import software.amazon.awssdk.auth.credentials.StaticCredentialsProvider;
import software.amazon.awssdk.regions.Region;
import software.amazon.awssdk.services.rds.RdsUtilities;
import software.amazon.awssdk.services.sts.StsClient;
import software.amazon.awssdk.services.sts.auth.StsAssumeRoleCredentialsProvider;
import software.amazon.awssdk.services.sts.model.AssumeRoleRequest;

/**
 * Authentication flow for AWS Aurora PostgreSQL using IAM Database Authentication.
 * 
 * This flow generates short-lived authentication tokens using AWS IAM credentials.
 * The token is used as the password when connecting to Aurora PostgreSQL databases
 * that have IAM database authentication enabled.
 * 
 * The generated tokens are valid for 15 minutes and can be reused during that period.
 * 
 * Prerequisites:
 * - Aurora cluster must have IAM database authentication enabled
 * - Database user must have rds_iam role granted
 * - IAM principal must have rds-db:connect permission
 */
public class AuroraPostgresWithIAMAuthFlow implements DatabaseAuthenticationFlow<AuroraPostgresDatasourceSpecification, AWSIAMDatabaseAuthenticationStrategy>
{
    @Override
    public Class<AuroraPostgresDatasourceSpecification> getDatasourceClass()
    {
        return AuroraPostgresDatasourceSpecification.class;
    }

    @Override
    public Class<AWSIAMDatabaseAuthenticationStrategy> getAuthenticationStrategyClass()
    {
        return AWSIAMDatabaseAuthenticationStrategy.class;
    }

    @Override
    public DatabaseType getDatabaseType()
    {
        // Aurora PostgreSQL is PostgreSQL-compatible
        return DatabaseType.Postgres;
    }

    @Override
    public Credential makeCredential(
            Identity identity,
            AuroraPostgresDatasourceSpecification datasourceSpecification,
            AWSIAMDatabaseAuthenticationStrategy authenticationStrategy) throws Exception
    {
        // Resolve AWS credentials based on the configured credential type
        AwsCredentialsProvider credentialsProvider = resolveAwsCredentials(
                authenticationStrategy.awsCredentials,
                datasourceSpecification.region
        );

        // Generate the IAM authentication token using AWS RDS utilities
        RdsUtilities rdsUtilities = RdsUtilities.builder()
                .region(Region.of(datasourceSpecification.region))
                .credentialsProvider(credentialsProvider)
                .build();

        String authToken = rdsUtilities.generateAuthenticationToken(builder -> builder
                .hostname(datasourceSpecification.host)
                .port(datasourceSpecification.port)
                .username(authenticationStrategy.databaseUsername)
        );

        // Return the credential with the database username and the IAM token as password
        return new PlaintextUserPasswordCredential(
                authenticationStrategy.databaseUsername,
                authToken
        );
    }

    /**
     * Resolves AWS credentials based on the configured credential type.
     *
     * @param awsCredentials The AWS credentials configuration
     * @param region The AWS region for STS operations
     * @return An AWS credentials provider
     */
    private AwsCredentialsProvider resolveAwsCredentials(AWSCredentials awsCredentials, String region) throws Exception
    {
        if (awsCredentials == null || awsCredentials instanceof AWSDefaultCredentials)
        {
            // Use the default AWS credential chain
            // This includes environment variables, system properties, 
            // credential files, instance profiles, etc.
            return DefaultCredentialsProvider.create();
        }

        if (awsCredentials instanceof AWSStaticCredentials)
        {
            AWSStaticCredentials staticCredentials = (AWSStaticCredentials) awsCredentials;
            
            // Resolve credentials from vault
            String accessKeyId = lookupSecret(staticCredentials.accessKeyId);
            String secretAccessKey = lookupSecret(staticCredentials.secretAccessKey);

            return StaticCredentialsProvider.create(
                    AwsBasicCredentials.create(accessKeyId, secretAccessKey)
            );
        }

        if (awsCredentials instanceof AWSSTSAssumeRoleCredentials)
        {
            AWSSTSAssumeRoleCredentials stsCredentials = (AWSSTSAssumeRoleCredentials) awsCredentials;
            
            // First, get the base credentials
            AwsCredentialsProvider baseProvider = resolveAwsCredentials(
                    stsCredentials.awsCredentials,
                    region
            );

            // Create STS client to assume the role
            StsClient stsClient = StsClient.builder()
                    .region(Region.of(region))
                    .credentialsProvider(baseProvider)
                    .build();

            // Build the assume role request
            AssumeRoleRequest assumeRoleRequest = AssumeRoleRequest.builder()
                    .roleArn(stsCredentials.roleArn)
                    .roleSessionName("legend-aurora-postgres-" + System.currentTimeMillis())
                    .build();

            // Return a credentials provider that assumes the role
            return StsAssumeRoleCredentialsProvider.builder()
                    .stsClient(stsClient)
                    .refreshRequest(assumeRoleRequest)
                    .build();
        }

        throw new UnsupportedOperationException(
                "Unsupported AWS credentials type: " + awsCredentials.getClass().getSimpleName()
        );
    }

    /**
     * Looks up a secret value from the vault.
     * Supports both CredentialVaultSecret types and plain string references.
     */
    private String lookupSecret(Object secret) throws Exception
    {
        if (secret == null)
        {
            throw new IllegalArgumentException("Secret reference cannot be null");
        }

        // Handle CredentialVaultSecret types
        if (secret instanceof org.finos.legend.engine.protocol.pure.v1.model.packageableElement.authentication.vault.CredentialVaultSecret)
        {
            org.finos.legend.engine.protocol.pure.v1.model.packageableElement.authentication.vault.CredentialVaultSecret vaultSecret =
                    (org.finos.legend.engine.protocol.pure.v1.model.packageableElement.authentication.vault.CredentialVaultSecret) secret;

            if (vaultSecret instanceof org.finos.legend.engine.protocol.pure.v1.model.packageableElement.authentication.vault.PropertiesFileSecret)
            {
                org.finos.legend.engine.protocol.pure.v1.model.packageableElement.authentication.vault.PropertiesFileSecret propsSecret =
                        (org.finos.legend.engine.protocol.pure.v1.model.packageableElement.authentication.vault.PropertiesFileSecret) vaultSecret;
                return Vault.INSTANCE.getValue(propsSecret.propertyName);
            }

            if (vaultSecret instanceof org.finos.legend.engine.protocol.pure.v1.model.packageableElement.authentication.vault.EnvironmentCredentialVaultSecret)
            {
                org.finos.legend.engine.protocol.pure.v1.model.packageableElement.authentication.vault.EnvironmentCredentialVaultSecret envSecret =
                        (org.finos.legend.engine.protocol.pure.v1.model.packageableElement.authentication.vault.EnvironmentCredentialVaultSecret) vaultSecret;
                String value = System.getenv(envSecret.envVariableName);
                if (value == null)
                {
                    throw new IllegalArgumentException("Environment variable not found: " + envSecret.envVariableName);
                }
                return value;
            }

            if (vaultSecret instanceof org.finos.legend.engine.protocol.pure.v1.model.packageableElement.authentication.vault.SystemPropertiesSecret)
            {
                org.finos.legend.engine.protocol.pure.v1.model.packageableElement.authentication.vault.SystemPropertiesSecret sysSecret =
                        (org.finos.legend.engine.protocol.pure.v1.model.packageableElement.authentication.vault.SystemPropertiesSecret) vaultSecret;
                String value = System.getProperty(sysSecret.systemPropertyName);
                if (value == null)
                {
                    throw new IllegalArgumentException("System property not found: " + sysSecret.systemPropertyName);
                }
                return value;
            }
        }

        throw new UnsupportedOperationException(
                "Unsupported secret type: " + secret.getClass().getSimpleName()
        );
    }
}

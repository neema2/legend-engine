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

package org.finos.legend.engine.language.pure.grammar.from;

import org.eclipse.collections.api.list.MutableList;
import org.eclipse.collections.impl.factory.Lists;
import org.finos.legend.engine.language.pure.grammar.from.antlr4.connection.AuroraPostgresLexerGrammar;
import org.finos.legend.engine.language.pure.grammar.from.antlr4.connection.AuroraPostgresParserGrammar;
import org.finos.legend.engine.language.pure.grammar.from.authentication.AuthenticationStrategySourceCode;
import org.finos.legend.engine.language.pure.grammar.from.datasource.DataSourceSpecificationSourceCode;
import org.finos.legend.engine.protocol.pure.v1.model.packageableElement.authentication.vault.aws.AWSCredentials;
import org.finos.legend.engine.protocol.pure.v1.model.packageableElement.authentication.vault.aws.AWSDefaultCredentials;
import org.finos.legend.engine.protocol.pure.v1.model.packageableElement.authentication.vault.aws.AWSSTSAssumeRoleCredentials;
import org.finos.legend.engine.protocol.pure.v1.model.packageableElement.authentication.vault.aws.AWSStaticCredentials;
import org.finos.legend.engine.protocol.pure.v1.model.packageableElement.authentication.vault.PropertiesFileSecret;
import org.finos.legend.engine.protocol.pure.v1.model.packageableElement.store.relational.connection.authentication.AWSIAMDatabaseAuthenticationStrategy;
import org.finos.legend.engine.protocol.pure.v1.model.packageableElement.store.relational.connection.authentication.AuthenticationStrategy;
import org.finos.legend.engine.protocol.pure.v1.model.packageableElement.store.relational.connection.specification.AuroraPostgresDatasourceSpecification;
import org.finos.legend.engine.protocol.pure.v1.model.packageableElement.store.relational.connection.specification.DatasourceSpecification;

import java.util.Collections;
import java.util.List;
import java.util.function.Function;

public class AuroraPostgresGrammarParserExtension implements IRelationalGrammarParserExtension
{
    @Override
    public MutableList<String> group()
    {
        return Lists.mutable.with("Store", "Relational", "AuroraPostgres");
    }

    @Override
    public List<Function<DataSourceSpecificationSourceCode, DatasourceSpecification>> getExtraDataSourceSpecificationParsers()
    {
        return Collections.singletonList(code ->
        {
            if ("AuroraPostgres".equals(code.getType()))
            {
                return IRelationalGrammarParserExtension.parse(
                        code,
                        AuroraPostgresLexerGrammar::new,
                        AuroraPostgresParserGrammar::new,
                        p -> visitAuroraPostgresDatasourceSpecification(p.auroraPostgresDatasourceSpecification())
                );
            }
            return null;
        });
    }

    @Override
    public List<Function<AuthenticationStrategySourceCode, AuthenticationStrategy>> getExtraAuthenticationStrategyParsers()
    {
        return Collections.singletonList(code ->
        {
            if ("AWSIAMDatabase".equals(code.getType()))
            {
                return IRelationalGrammarParserExtension.parse(
                        code,
                        AuroraPostgresLexerGrammar::new,
                        AuroraPostgresParserGrammar::new,
                        p -> visitAWSIAMDatabaseAuthenticationStrategy(p.awsIAMDatabaseAuthenticationStrategy())
                );
            }
            return null;
        });
    }

    private AuroraPostgresDatasourceSpecification visitAuroraPostgresDatasourceSpecification(
            AuroraPostgresParserGrammar.AuroraPostgresDatasourceSpecificationContext ctx)
    {
        AuroraPostgresDatasourceSpecification spec = new AuroraPostgresDatasourceSpecification();

        AuroraPostgresParserGrammar.DbHostContext hostCtx = 
                PureGrammarParserUtility.validateAndExtractRequiredField(ctx.dbHost(), "host", spec.sourceInformation);
        AuroraPostgresParserGrammar.DbPortContext portCtx = 
                PureGrammarParserUtility.validateAndExtractRequiredField(ctx.dbPort(), "port", spec.sourceInformation);
        AuroraPostgresParserGrammar.DbNameContext nameCtx = 
                PureGrammarParserUtility.validateAndExtractRequiredField(ctx.dbName(), "name", spec.sourceInformation);
        AuroraPostgresParserGrammar.RegionContext regionCtx = 
                PureGrammarParserUtility.validateAndExtractRequiredField(ctx.region(), "region", spec.sourceInformation);
        AuroraPostgresParserGrammar.ClusterIdentifierContext clusterCtx = 
                PureGrammarParserUtility.validateAndExtractOptionalField(ctx.clusterIdentifier(), "clusterIdentifier", spec.sourceInformation);

        spec.host = PureGrammarParserUtility.fromGrammarString(hostCtx.STRING().getText(), true);
        spec.port = Integer.parseInt(portCtx.INTEGER().getText());
        spec.databaseName = PureGrammarParserUtility.fromGrammarString(nameCtx.STRING().getText(), true);
        spec.region = PureGrammarParserUtility.fromGrammarString(regionCtx.STRING().getText(), true);
        
        if (clusterCtx != null)
        {
            spec.clusterIdentifier = PureGrammarParserUtility.fromGrammarString(clusterCtx.STRING().getText(), true);
        }

        return spec;
    }

    private AWSIAMDatabaseAuthenticationStrategy visitAWSIAMDatabaseAuthenticationStrategy(
            AuroraPostgresParserGrammar.AwsIAMDatabaseAuthenticationStrategyContext ctx)
    {
        AWSIAMDatabaseAuthenticationStrategy strategy = new AWSIAMDatabaseAuthenticationStrategy();

        AuroraPostgresParserGrammar.DatabaseUsernameContext usernameCtx = 
                PureGrammarParserUtility.validateAndExtractRequiredField(ctx.databaseUsername(), "databaseUsername", strategy.sourceInformation);
        AuroraPostgresParserGrammar.AwsCredentialsContext credentialsCtx = 
                PureGrammarParserUtility.validateAndExtractOptionalField(ctx.awsCredentials(), "awsCredentials", strategy.sourceInformation);

        strategy.databaseUsername = PureGrammarParserUtility.fromGrammarString(usernameCtx.STRING().getText(), true);
        
        if (credentialsCtx != null)
        {
            strategy.awsCredentials = visitAwsCredentials(credentialsCtx.awsCredentialsValue());
        }
        else
        {
            // Default to AWSDefaultCredentials if not specified
            strategy.awsCredentials = new AWSDefaultCredentials();
        }

        return strategy;
    }

    private AWSCredentials visitAwsCredentials(AuroraPostgresParserGrammar.AwsCredentialsValueContext ctx)
    {
        if (ctx.awsDefaultCredentials() != null)
        {
            return new AWSDefaultCredentials();
        }
        if (ctx.awsStaticCredentials() != null)
        {
            return visitAwsStaticCredentials(ctx.awsStaticCredentials());
        }
        if (ctx.awsStsAssumeRoleCredentials() != null)
        {
            return visitAwsStsAssumeRoleCredentials(ctx.awsStsAssumeRoleCredentials());
        }
        throw new RuntimeException("Unsupported AWS credentials type");
    }

    private AWSStaticCredentials visitAwsStaticCredentials(AuroraPostgresParserGrammar.AwsStaticCredentialsContext ctx)
    {
        AWSStaticCredentials credentials = new AWSStaticCredentials();

        AuroraPostgresParserGrammar.AccessKeyIdContext accessKeyCtx = 
                PureGrammarParserUtility.validateAndExtractRequiredField(ctx.accessKeyId(), "accessKeyId", null);
        AuroraPostgresParserGrammar.SecretAccessKeyContext secretKeyCtx = 
                PureGrammarParserUtility.validateAndExtractRequiredField(ctx.secretAccessKey(), "secretAccessKey", null);

        // For now, use PropertiesFileSecret for the vault references
        PropertiesFileSecret accessKeySecret = new PropertiesFileSecret();
        accessKeySecret.propertyName = PureGrammarParserUtility.fromGrammarString(accessKeyCtx.STRING().getText(), true);
        credentials.accessKeyId = accessKeySecret;

        PropertiesFileSecret secretKeySecret = new PropertiesFileSecret();
        secretKeySecret.propertyName = PureGrammarParserUtility.fromGrammarString(secretKeyCtx.STRING().getText(), true);
        credentials.secretAccessKey = secretKeySecret;

        return credentials;
    }

    private AWSSTSAssumeRoleCredentials visitAwsStsAssumeRoleCredentials(AuroraPostgresParserGrammar.AwsStsAssumeRoleCredentialsContext ctx)
    {
        AWSSTSAssumeRoleCredentials credentials = new AWSSTSAssumeRoleCredentials();

        AuroraPostgresParserGrammar.RoleArnContext roleArnCtx = 
                PureGrammarParserUtility.validateAndExtractRequiredField(ctx.roleArn(), "roleArn", null);
        AuroraPostgresParserGrammar.AwsCredentialsContext baseCredentialsCtx = 
                PureGrammarParserUtility.validateAndExtractOptionalField(ctx.awsCredentials(), "awsCredentials", null);

        credentials.roleArn = PureGrammarParserUtility.fromGrammarString(roleArnCtx.STRING().getText(), true);
        
        if (baseCredentialsCtx != null)
        {
            credentials.awsCredentials = visitAwsCredentials(baseCredentialsCtx.awsCredentialsValue());
        }
        else
        {
            credentials.awsCredentials = new AWSDefaultCredentials();
        }

        return credentials;
    }
}

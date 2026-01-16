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

package org.finos.legend.engine.language.pure.grammar.to;

import org.eclipse.collections.api.block.function.Function2;
import org.eclipse.collections.api.list.MutableList;
import org.eclipse.collections.impl.factory.Lists;
import org.finos.legend.engine.protocol.pure.v1.model.packageableElement.authentication.vault.aws.AWSCredentials;
import org.finos.legend.engine.protocol.pure.v1.model.packageableElement.authentication.vault.aws.AWSDefaultCredentials;
import org.finos.legend.engine.protocol.pure.v1.model.packageableElement.authentication.vault.aws.AWSSTSAssumeRoleCredentials;
import org.finos.legend.engine.protocol.pure.v1.model.packageableElement.authentication.vault.aws.AWSStaticCredentials;
import org.finos.legend.engine.protocol.pure.v1.model.packageableElement.authentication.vault.CredentialVaultSecret;
import org.finos.legend.engine.protocol.pure.v1.model.packageableElement.authentication.vault.PropertiesFileSecret;
import org.finos.legend.engine.protocol.pure.v1.model.packageableElement.store.relational.connection.authentication.AWSIAMDatabaseAuthenticationStrategy;
import org.finos.legend.engine.protocol.pure.v1.model.packageableElement.store.relational.connection.authentication.AuthenticationStrategy;
import org.finos.legend.engine.protocol.pure.v1.model.packageableElement.store.relational.connection.specification.AuroraPostgresDatasourceSpecification;
import org.finos.legend.engine.protocol.pure.v1.model.packageableElement.store.relational.connection.specification.DatasourceSpecification;

import java.util.List;

import static org.finos.legend.engine.language.pure.grammar.to.PureGrammarComposerUtility.convertString;
import static org.finos.legend.engine.language.pure.grammar.to.PureGrammarComposerUtility.getTabString;

public class AuroraPostgresGrammarComposerExtension implements IRelationalGrammarComposerExtension
{
    @Override
    public MutableList<String> group()
    {
        return Lists.mutable.with("Store", "Relational", "AuroraPostgres");
    }

    @Override
    public List<Function2<DatasourceSpecification, PureGrammarComposerContext, String>> getExtraDataSourceSpecificationComposers()
    {
        return Lists.mutable.with((spec, context) ->
        {
            if (spec instanceof AuroraPostgresDatasourceSpecification)
            {
                AuroraPostgresDatasourceSpecification auroraSpec = (AuroraPostgresDatasourceSpecification) spec;
                int baseIndentation = 1;
                StringBuilder builder = new StringBuilder();
                builder.append("AuroraPostgres\n");
                builder.append(context.getIndentationString()).append(getTabString(baseIndentation)).append("{\n");
                builder.append(context.getIndentationString()).append(getTabString(baseIndentation + 1)).append("host: ").append(convertString(auroraSpec.host, true)).append(";\n");
                builder.append(context.getIndentationString()).append(getTabString(baseIndentation + 1)).append("port: ").append(auroraSpec.port).append(";\n");
                builder.append(context.getIndentationString()).append(getTabString(baseIndentation + 1)).append("name: ").append(convertString(auroraSpec.databaseName, true)).append(";\n");
                builder.append(context.getIndentationString()).append(getTabString(baseIndentation + 1)).append("region: ").append(convertString(auroraSpec.region, true)).append(";\n");
                if (auroraSpec.clusterIdentifier != null && !auroraSpec.clusterIdentifier.isEmpty())
                {
                    builder.append(context.getIndentationString()).append(getTabString(baseIndentation + 1)).append("clusterIdentifier: ").append(convertString(auroraSpec.clusterIdentifier, true)).append(";\n");
                }
                builder.append(context.getIndentationString()).append(getTabString(baseIndentation)).append("}");
                return builder.toString();
            }
            return null;
        });
    }

    @Override
    public List<Function2<AuthenticationStrategy, PureGrammarComposerContext, String>> getExtraAuthenticationStrategyComposers()
    {
        return Lists.mutable.with((strategy, context) ->
        {
            if (strategy instanceof AWSIAMDatabaseAuthenticationStrategy)
            {
                AWSIAMDatabaseAuthenticationStrategy iamStrategy = (AWSIAMDatabaseAuthenticationStrategy) strategy;
                int baseIndentation = 1;
                StringBuilder builder = new StringBuilder();
                builder.append("AWSIAMDatabase\n");
                builder.append(context.getIndentationString()).append(getTabString(baseIndentation)).append("{\n");
                builder.append(context.getIndentationString()).append(getTabString(baseIndentation + 1)).append("databaseUsername: ").append(convertString(iamStrategy.databaseUsername, true)).append(";\n");
                if (iamStrategy.awsCredentials != null)
                {
                    builder.append(context.getIndentationString()).append(getTabString(baseIndentation + 1)).append("awsCredentials: ");
                    builder.append(composeAwsCredentials(iamStrategy.awsCredentials, context, baseIndentation + 1));
                    builder.append(";\n");
                }
                builder.append(context.getIndentationString()).append(getTabString(baseIndentation)).append("}");
                return builder.toString();
            }
            return null;
        });
    }

    private String composeAwsCredentials(AWSCredentials credentials, PureGrammarComposerContext context, int indentation)
    {
        if (credentials instanceof AWSDefaultCredentials)
        {
            return "Default {}";
        }
        if (credentials instanceof AWSStaticCredentials)
        {
            AWSStaticCredentials staticCreds = (AWSStaticCredentials) credentials;
            StringBuilder builder = new StringBuilder();
            builder.append("Static\n");
            builder.append(context.getIndentationString()).append(getTabString(indentation + 1)).append("{\n");
            builder.append(context.getIndentationString()).append(getTabString(indentation + 2)).append("accessKeyId: ").append(composeSecret(staticCreds.accessKeyId)).append(";\n");
            builder.append(context.getIndentationString()).append(getTabString(indentation + 2)).append("secretAccessKey: ").append(composeSecret(staticCreds.secretAccessKey)).append(";\n");
            builder.append(context.getIndentationString()).append(getTabString(indentation + 1)).append("}");
            return builder.toString();
        }
        if (credentials instanceof AWSSTSAssumeRoleCredentials)
        {
            AWSSTSAssumeRoleCredentials stsCreds = (AWSSTSAssumeRoleCredentials) credentials;
            StringBuilder builder = new StringBuilder();
            builder.append("STSAssumeRole\n");
            builder.append(context.getIndentationString()).append(getTabString(indentation + 1)).append("{\n");
            builder.append(context.getIndentationString()).append(getTabString(indentation + 2)).append("roleArn: ").append(convertString(stsCreds.roleArn, true)).append(";\n");
            if (stsCreds.awsCredentials != null)
            {
                builder.append(context.getIndentationString()).append(getTabString(indentation + 2)).append("awsCredentials: ");
                builder.append(composeAwsCredentials(stsCreds.awsCredentials, context, indentation + 2));
                builder.append(";\n");
            }
            builder.append(context.getIndentationString()).append(getTabString(indentation + 1)).append("}");
            return builder.toString();
        }
        throw new RuntimeException("Unsupported AWS credentials type: " + credentials.getClass().getSimpleName());
    }

    private String composeSecret(CredentialVaultSecret secret)
    {
        if (secret instanceof PropertiesFileSecret)
        {
            return convertString(((PropertiesFileSecret) secret).propertyName, true);
        }
        throw new RuntimeException("Unsupported secret type: " + secret.getClass().getSimpleName());
    }
}

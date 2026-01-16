parser grammar AuroraPostgresParserGrammar;

import CoreParserGrammar;

options
{
    tokenVocab = AuroraPostgresLexerGrammar;
}

// ----------------------------- Aurora PostgreSQL Datasource Specification -----------------------------

auroraPostgresDatasourceSpecification:  AURORA_POSTGRES
                                        BRACE_OPEN
                                            (
                                                dbHost
                                                | dbPort
                                                | dbName
                                                | region
                                                | clusterIdentifier
                                            )*
                                        BRACE_CLOSE
;

dbHost:                                 HOST COLON STRING SEMI_COLON
;

dbPort:                                 PORT COLON INTEGER SEMI_COLON
;

dbName:                                 NAME COLON STRING SEMI_COLON
;

region:                                 REGION COLON STRING SEMI_COLON
;

clusterIdentifier:                      CLUSTER_IDENTIFIER COLON STRING SEMI_COLON
;

// ----------------------------- AWS IAM Database Authentication Strategy -----------------------------

awsIAMDatabaseAuthenticationStrategy:   AWS_IAM_DATABASE
                                        BRACE_OPEN
                                            (
                                                databaseUsername
                                                | awsCredentials
                                            )*
                                        BRACE_CLOSE
;

databaseUsername:                       DATABASE_USERNAME COLON STRING SEMI_COLON
;

awsCredentials:                         AWS_CREDENTIALS COLON awsCredentialsValue SEMI_COLON
;

awsCredentialsValue:                    awsDefaultCredentials
                                        | awsStaticCredentials
                                        | awsStsAssumeRoleCredentials
;

awsDefaultCredentials:                  DEFAULT BRACE_OPEN BRACE_CLOSE
;

awsStaticCredentials:                   STATIC
                                        BRACE_OPEN
                                            (
                                                accessKeyId
                                                | secretAccessKey
                                            )*
                                        BRACE_CLOSE
;

awsStsAssumeRoleCredentials:            STS_ASSUME_ROLE
                                        BRACE_OPEN
                                            (
                                                roleArn
                                                | awsCredentials
                                            )*
                                        BRACE_CLOSE
;

accessKeyId:                            ACCESS_KEY_ID COLON STRING SEMI_COLON
;

secretAccessKey:                        SECRET_ACCESS_KEY COLON STRING SEMI_COLON
;

roleArn:                                ROLE_ARN COLON STRING SEMI_COLON
;

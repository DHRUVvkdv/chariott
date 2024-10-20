import * as cdk from 'aws-cdk-lib';
import { Construct } from 'constructs';
import * as lambda from 'aws-cdk-lib/aws-lambda'
import * as iam from 'aws-cdk-lib/aws-iam';
import * as dotenv from 'dotenv';
import * as dynamodb from 'aws-cdk-lib/aws-dynamodb';

// Load environment variables from .env file
dotenv.config();

export class CodefestBackendInfraStack extends cdk.Stack {
  constructor(scope: Construct, id: string, props?: cdk.StackProps) {
    super(scope, id, props);

    const PRIVATE_AWS_ACCESS_KEY_ID = process.env.PRIVATE_AWS_ACCESS_KEY_ID;
    if (!PRIVATE_AWS_ACCESS_KEY_ID) {
      throw new Error("PRIVATE_AWS_ACCESS_KEY_ID environment variable is not set");
    }
    const PRIVATE_AWS_SECRET_ACCESS_KEY = process.env.PRIVATE_AWS_SECRET_ACCESS_KEY;
    if (!PRIVATE_AWS_SECRET_ACCESS_KEY) {
      throw new Error("PRIVATE_AWS_SECRET_ACCESS_KEY environment variable is not set");
    }
    const PRIVATE_AWS_REGION = process.env.PRIVATE_AWS_REGION;
    if (!PRIVATE_AWS_REGION) {
      throw new Error("PRIVATE_AWS_REGION environment variable is not set");
    }
    const S3_BUCKET_NAME = process.env.S3_BUCKET_NAME;
    if (!S3_BUCKET_NAME) {
      throw new Error("S3_BUCKET_NAME environment variable is not set");
    }
    const API_KEY = process.env.API_KEY;
    if (!API_KEY) {
      throw new Error("API_KEY environment variable is not set");
    }
    const COGNITO_USER_POOL_ID = process.env.COGNITO_USER_POOL_ID;
    if (!COGNITO_USER_POOL_ID) {
      throw new Error("COGNITO_USER_POOL_ID environment variable is not set");
    }
    const COGNITO_APP_CLIENT_ID = process.env.COGNITO_APP_CLIENT_ID;
    if (!COGNITO_APP_CLIENT_ID) {
      throw new Error("COGNITO_APP_CLIENT_ID environment variable is not set");
    }
    const DYNAMODB_TABLE_NAME_USERS = process.env.DYNAMODB_TABLE_NAME_USERS;
    if (!DYNAMODB_TABLE_NAME_USERS) {
      throw new Error("DYNAMODB_TABLE_NAME_USERS environment variable is not set");
    }
    const DYNAMODB_TABLE_NAME_PROCESSED_FILES = process.env.DYNAMODB_TABLE_NAME_PROCESSED_FILES;
    if (!DYNAMODB_TABLE_NAME_PROCESSED_FILES) {
      throw new Error("DYNAMODB_TABLE_NAME_PROCESSED_FILES environment variable is not set");
    }
    const DYNAMODB_TABLE_NAME_REQUESTS = process.env.DYNAMODB_TABLE_NAME_REQUESTS;
    if (!DYNAMODB_TABLE_NAME_REQUESTS) {
      throw new Error("DYNAMODB_TABLE_NAME_REQUESTS environment variable is not set");
    }
    const PINECONE_API_KEY = process.env.PINECONE_API_KEY;
    if (!PINECONE_API_KEY) {
      throw new Error("PINECONE_API_KEY environment variable is not set");
    }
    const PINECONE_INDEX_NAME = process.env.PINECONE_INDEX_NAME;
    if (!PINECONE_INDEX_NAME) {
      throw new Error("PINECONE_INDEX_NAME environment variable is not set");
    }


    // Create a Lambda function from a Docker image
    const apiFunction = new lambda.DockerImageFunction(this, 'ApiFunction', {
      code: lambda.DockerImageCode.fromImageAsset('../image', {
        cmd: ["main.handler"]
      }),
      memorySize: 512,
      timeout: cdk.Duration.seconds(60),
      architecture: lambda.Architecture.ARM_64,
      environment: {
        PRIVATE_AWS_ACCESS_KEY_ID,
        PRIVATE_AWS_SECRET_ACCESS_KEY,
        PRIVATE_AWS_REGION,
        S3_BUCKET_NAME,
        API_KEY,
        COGNITO_USER_POOL_ID,
        COGNITO_APP_CLIENT_ID,
        DYNAMODB_TABLE_NAME_USERS,
        DYNAMODB_TABLE_NAME_PROCESSED_FILES,
        PINECONE_API_KEY,
        PINECONE_INDEX_NAME,
        DYNAMODB_TABLE_NAME_REQUESTS
      },
    });

    apiFunction.role?.addManagedPolicy(
      iam.ManagedPolicy.fromAwsManagedPolicyName('AmazonCognitoPowerUser')
    );

        // Grant DynamoDB permissions
        const table_users = dynamodb.Table.fromTableName(this, 'UsersTable', DYNAMODB_TABLE_NAME_USERS);
        table_users.grantReadWriteData(apiFunction);
    
        const table_processed_files = dynamodb.Table.fromTableName(this, 'ProcessedFilesTable', DYNAMODB_TABLE_NAME_PROCESSED_FILES);
        table_processed_files.grantReadWriteData(apiFunction);

        const table_requests = dynamodb.Table.fromTableName(this, 'RequestsTable', DYNAMODB_TABLE_NAME_REQUESTS);
        table_requests.grantReadWriteData(apiFunction);


            // Grant additional permissions for GSI querying
    apiFunction.addToRolePolicy(new iam.PolicyStatement({
      effect: iam.Effect.ALLOW,
      actions: [
        'dynamodb:Query',
        'dynamodb:Scan'
      ],
      resources: [
        `${table_requests.tableArn}/index/*`,
        `${table_users.tableArn}/index/*`,
        `${table_processed_files.tableArn}/index/*`
      ]
    }));

    // Add a function URL to the Lambda
    const functionUrl = apiFunction.addFunctionUrl({
      authType: lambda.FunctionUrlAuthType.NONE, // This makes it publicly accessible
    });

    // Add Bedrock permissions
    apiFunction.addToRolePolicy(new iam.PolicyStatement({
      effect: iam.Effect.ALLOW,
      actions: ['bedrock:InvokeModel'],
      resources: ['arn:aws:bedrock:us-east-1::foundation-model/amazon.titan-embed-text-v1'],
    }));

    // Output the Function URL
    new cdk.CfnOutput(this, 'FunctionUrl', {
      value: functionUrl.url,
      description: 'URL for the Lambda function',
    });
  }
}
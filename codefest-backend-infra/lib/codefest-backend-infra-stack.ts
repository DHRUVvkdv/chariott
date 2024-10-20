import * as cdk from 'aws-cdk-lib';
import { Construct } from 'constructs';
import * as lambda from 'aws-cdk-lib/aws-lambda';
import * as path from 'path';
import * as dotenv from 'dotenv';

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
    const DYNAMODB_TABLE_NAME = process.env.DYNAMODB_TABLE_NAME;
    if (!DYNAMODB_TABLE_NAME) {
      throw new Error("DYNAMODB_TABLE_NAME environment variable is not set");
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
      },
    });

    // Add a function URL to the Lambda
    const functionUrl = apiFunction.addFunctionUrl({
      authType: lambda.FunctionUrlAuthType.NONE, // This makes it publicly accessible
    });

    // Output the Function URL
    new cdk.CfnOutput(this, 'FunctionUrl', {
      value: functionUrl.url,
      description: 'URL for the Lambda function',
    });
  }
}
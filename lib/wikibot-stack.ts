import { Construct } from 'constructs';
import {
  Stack, StackProps,
  CfnOutput, pipelines,
  aws_lambda as lambda
} from 'aws-cdk-lib';
import { FunctionUrlAuthType } from 'aws-cdk-lib/aws-lambda';

// TODO: put credentials into parameter store secrets, cache these secrets in the lambda function
// TODO: create a lambda layer for the Slack and together.ai/OpenAI python libraries

export class WikibotStack extends Stack {
  constructor(scope: Construct, id: string, props?: StackProps) {
    super(scope, id, props);

    /// This Code block defines an AWS codepipeline that regenerates this stack when commits are merged to the main branch
    // const pipeline = new pipelines.CodePipeline(this, 'Pipeline', {
    //   pipelineName: 'Denhac-WikiBot',
    //   synth: new pipelines.ShellStep('Synth', {
    //     input: pipelines.CodePipelineSource.gitHub('Denhac/wikibot', 'main'),
    //     commands: ['npm ci', 'npm run build', 'npx cdk synth']
    //   })
    // }); UNCOMMENT IN 'PRODUCTION'
    /// End Pipeline codeblock

    /// Chatbot infrastructure
    // Validate Slack events, trigger the generateReply function, quickly reply to Slack
    const webhook = new lambda.Function(this, "SlackWebhook", {
      functionName: "WikiBot-SlackWebhook",
      runtime: lambda.Runtime.PYTHON_3_12,
      handler: "slackWebhook.handler",
      code: lambda.Code.fromAsset('./lambda/slackWebhook')
    })
    const slackEndoint = webhook.addFunctionUrl({
      authType: FunctionUrlAuthType.NONE,
      cors: { allowedOrigins: ['https://api.slack.com'], allowedHeaders: ["*"] }
    })
    new CfnOutput(this, "WebhookURL", { value: slackEndoint.url }) //Print the function URL to the command line after deployment

    // Perform vector search, Generate a reply based on the user's input and the wiki text
    const generateReply = new lambda.Function(this, "GenerateReply", {
      functionName: "WikiBot-GenerateReply",
      runtime: lambda.Runtime.PYTHON_3_12,
      handler: "generateReply.handler",
      code: lambda.Code.fromAsset('./lambda/generateReply')
    })
  }
}

import { Construct } from 'constructs';
import {
  Stack, StackProps, Duration,
  CfnOutput, pipelines,
  aws_lambda as lambda,
  aws_events as events,
  aws_events_targets as targets
} from 'aws-cdk-lib';
import { FunctionUrlAuthType } from 'aws-cdk-lib/aws-lambda';

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
    // Import lambda layers
    const AiLayer = lambda.LayerVersion.fromLayerVersionArn(this, "AILayer", "arn:aws:lambda:us-east-2:526411345739:layer:openAI:3")
    const slackLayer = lambda.LayerVersion.fromLayerVersionArn(this, "slackLayer", "arn:aws:lambda:us-east-2:526411345739:layer:slack:4")
    const mongodbLayer = lambda.LayerVersion.fromLayerVersionArn(this, "mongoLayer", "arn:aws:lambda:us-east-2:526411345739:layer:pymongo:6")
    const beautifulLayer = lambda.LayerVersion.fromLayerVersionArn(this, "beautifulLayer", "arn:aws:lambda:us-east-2:526411345739:layer:beautifulsoup4:8")

    // Validate Slack events, trigger the generateReply function, quickly reply to Slack
    const webhook = new lambda.Function(this, "SlackWebhook", {
      functionName: "WikiBot-SlackWebhook",
      runtime: lambda.Runtime.PYTHON_3_11,
      handler: "slackWebhook.handler",
      code: lambda.Code.fromAsset('./lambda/slackWebhook'),
      layers: [slackLayer]
    })
    const slackEndoint = webhook.addFunctionUrl({
      authType: FunctionUrlAuthType.NONE,
      cors: { allowedOrigins: ['https://api.slack.com'], allowedHeaders: ["*"] }
    })
    new CfnOutput(this, "WebhookURL", { value: slackEndoint.url }) //Print the function URL to the command line after deployment

    // Perform vector search, Generate a reply based on the user's input and the wiki text
    const generateReply = new lambda.Function(this, "GenerateReply", {
      functionName: "WikiBot-GenerateReply",
      runtime: lambda.Runtime.PYTHON_3_11,
      handler: "generateReply.handler",
      code: lambda.Code.fromAsset('./lambda/generateReply'),
      layers: [AiLayer, mongodbLayer, slackLayer],
      timeout: Duration.seconds(30)
    })
    generateReply.grantInvoke(webhook)
    
    // Fetch updates to the wiki and update the embeddings as well
    const populateDatabase = new lambda.Function(this, "PopulateDatabase", {
      functionName: "WikiBot-PopulateDatabase",
      runtime: lambda.Runtime.PYTHON_3_11,
      handler: "populateDatabase.handler",
      code: lambda.Code.fromAsset('./lambda/populateDatabase'),
      layers: [AiLayer, mongodbLayer, beautifulLayer],
      timeout: Duration.seconds(30)
    })

    // Create an EventBridge rule to trigger the function every day at midnight
    const rule = new events.Rule(this, 'TriggerUpdates', {
      schedule: events.Schedule.cron({ minute: '0', hour: '0', weekDay: "Monday" }),
      targets: [new targets.LambdaFunction(populateDatabase)]
    });

    // Print the function ARNs that need to be listed on the 'Database Access' tab of the mongodb dashboard
    new CfnOutput(this, "UpdateFunctionRole", { value: populateDatabase.role?.roleArn ?? "Update Function Role Not Found" })
    new CfnOutput(this, "GenerateFunctionRole", { value: generateReply.role?.roleArn ?? "Generate Function Role Not Found" })
  }
}

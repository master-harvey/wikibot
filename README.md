# WikiBot - a RAG powered chatbot

Uses [MongoDB Atlas](https://www.mongodb.com/atlas/database), [Together.ai](together.ai), and hosted using AWS lambda with a Slackbot interface.

Influenced heavily by [this](https://www.together.ai/blog/rag-tutorial-mongodb) guide to a RAG chatbot.

Infrastructure as Code generated with [the AWS CDK](https://docs.aws.amazon.com/cdk/v2/guide/home.html).

## Development roadmap

* [X] Create a webhook for Slack that passes the challenge verification
* [X] Create lambda layers for the slack, mongodb, and togetherai libraries
* [ ] Validate Slack events in the first function
* [X] Lambda function chaining (asynchronously invoke the second function before returning a 200 reply to slack)
* [X] Deploy Database
* [X] Devise a database population mechanism (nightly lambda that pushes changes from the wiki to the database)
  * [X] Queries for updates
  * [ ] Respond to deleted articles
* [X] LLM integration in the second function
* [ ] Reply over Slack
  * [X] Slack workspace endpoint requested

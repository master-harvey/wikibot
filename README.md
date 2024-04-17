# WikiBot - a RAG powered chatbot

Uses [MongoDB Atlas](https://www.mongodb.com/atlas/database), [Together.ai](together.ai), and hosted using AWS lambda with a Slackbot interface.

Influenced heavily by [this](https://www.together.ai/blog/rag-tutorial-mongodb) guide to a RAG chatbot.

Infrastructure as Code generated with [the AWS CDK](https://docs.aws.amazon.com/cdk/v2/guide/home.html).

## Development roadmap

* [X] Create a Slack webhook that passes the challenge verification
* [ ] Create lambda layers for the slack and openai libraries
* [ ] Validate Slack events in the first function
* [ ] Lambda function chaining (asynchronously invoke the second function before returning a 200 reply to slack)
* [ ] Deploy Database
* [ ] Devise a database population mechanism (nightly lambda that pushes changes from the wiki to the database?)
* [ ] LLM integration in the second function
* [ ] Reply over Slack
  * [X] Slack webhook requested

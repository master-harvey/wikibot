# WikiBot - a RAG powered chatbot

Uses [MongoDB Atlas](https://www.mongodb.com/atlas/database), [Together.ai](together.ai), and hosted using AWS lambda with a Slackbot interface.

Influenced heavily by [this](https://www.together.ai/blog/rag-tutorial-mongodb) guide to a RAG chatbot.

Infrastructure as Code generated with [the AWS CDK](https://docs.aws.amazon.com/cdk/v2/guide/home.html).

## Development roadmap

* [X] RAG Powered Chatbot in Slack
  * [ ] Fill the rest of the context window with the preceding conversation
* [ ] Populate the database
  * [ ] Respond to updates

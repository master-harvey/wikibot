# WikiBot - a RAG powered chatbot

Uses [MongoDB Atlas](https://www.mongodb.com/atlas/database), [Together.ai](together.ai), and hosted using AWS lambda with a Slackbot interface.

Influenced heavily by [this ](https://www.mongodb.com/library/vector-search/rag-atlas-vector-search-langchain-openai?lb-mode=overlay)Mongodb guide to a RAG chatbot.

Infrastructure as Code generated with [the AWS CDK](https://docs.aws.amazon.com/cdk/v2/guide/home.html).

## Development roadmap

* [X] Create a Slack webhook that passes the challenge verification
* [ ] Validate Slack events in the first function
* [ ] Lambda function chaining
* [ ] RAG Pipeline
  * [ ] Deploy Database
  * [ ] Populate Database
  * [ ] LLM stuff in the second function
* [ ] Reply over Slack
  * [X] Slack webhook requested

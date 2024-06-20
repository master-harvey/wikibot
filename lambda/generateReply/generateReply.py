from json import loads, dumps
import os
from openai import OpenAI
from pymongo import MongoClient
import urllib3
import urllib.parse

mongo = MongoClient(os.environ["MONGODB_URI"]
        .replace('<session token (for AWS IAM Roles)>',urllib.parse.quote_plus(os.environ["AWS_SESSION_TOKEN"]))
        .replace('<AWS access key>',urllib.parse.quote_plus(os.environ["AWS_ACCESS_KEY_ID"]))
        .replace('<AWS secret key>',urllib.parse.quote_plus(os.environ["AWS_SECRET_ACCESS_KEY"]))
)
AI = OpenAI(api_key=os.environ["TOGETHER_API_KEY"], base_url='https://api.together.ai/v1')
http = urllib3.PoolManager()

embedding_model_string = 'togethercomputer/m2-bert-80M-8k-retrieval' # model API string from Together.
vector_database_field_name = 'embedding_together_m2-bert-8k-retrieval' # define your embedding/index field name.
query_model_string = 'meta-llama/Llama-3-8b-chat-hf' # model API string from Together.

def handler(event,context):
    """The lambda handler that will actually query the database and send a reply over Slack"""
    # print("EVENT: ",event," :EVENT")
    # print("CONTEXT: ",context," :CONTEXT")
    try:
      event = loads(event['body']) #convert plain text json to python dictionary
    except:
      event = event['body']

    # Query the database https://www.mongodb.com/docs/atlas/atlas-vector-search/vector-search-stage/
    message_embedding = AI.embeddings.create(input=event['event']['text'], model=embedding_model_string).data[0].embedding
    
    search_results = list(mongo.Denhac_Wiki.Articles.aggregate([
      {
        "$vectorSearch": {
          "index": "vector_embeddings",
          "queryVector": message_embedding,
          "path": vector_database_field_name,
          "numCandidates": 45, # this should be 10-20x the limit
          "limit": 3, # the number of documents to return in the results
        } # https://docs.together.ai/docs/inference-models
      } # The largest articles have ~2100 tokens so an 8k context model should accurately interpret 3 articles + the user's query
    ]))

    # BIG AI STUFF
    prompt = "You are a helpful digital assistant made to answer questions about the Denhac Hackerspace. "
    "Based on the user's query and relevant articles from the hackerspace wiki, provide the most complete, helpful, and concise answer possible. "
    "If the prompt pertains to Denhac's facilities but the answer is not contained in the wiki, do not try to guess the correct information about Denhac and instead inform the user that you do not know. "
    
    ai_response = AI.chat.completions.create(
      messages=[
        {
          "role": "prompt",
          "content": prompt
        },
        {
          "role": "user",
          "content": event['event']['text']
        },
        {
          "role": "system",
          "content": "<Wiki Articles>\n" + "\n\n----------\n\n".join(["Title: " + article['title'] + "\n" + article['content'] for article in search_results]) + "</Wiki Articles>\n"
        }
      ],
      model=query_model_string,
        temperature = 0.1,
        # max_tokens = 512,
        # top_k = 60,
        # top_p = 0.6,
        # repetition_penalty = 1.1,
        # stop = stop_sequences
    )
    # print(ai_response.choices[0].message.content)

    # Send the reply over slack
    ### send slack this: response.choices[0].message.content
    slack_response = http.request('POST', "https://slack.com/api/chat.postMessage",
      headers={"Content-Type":"application/json", "Authorization":"Bearer "+os.environ['SLACK_OAUTH_TOKEN']},
      body=dumps({"channel":event['event']['channel'],
                  "thread_ts":event['event']['ts'], #always reply in thread, new thread for a new conversation
                  "text":ai_response.choices[0].message.content
                })
    )
    print("Slack Response: ", slack_response.status, slack_response.reason)
    
    print("Big Success: " + ai_response.choices[0].message.content)
    return "Big Success: " + ai_response.choices[0].message.content
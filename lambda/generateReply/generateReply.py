from json import loads
import os
from together import Together
from pymongo import MongoClient

mongo = MongoClient(host=os.environ["MONGODB_URI"])
together = Together(api_key=os.environ["TOGETHER_API_KEY"])

embedding_model_string = 'togethercomputer/m2-bert-80M-8k-retrieval' # model API string from Together.
vector_database_field_name = 'embedding_together_m2-bert-8k-retrieval' # define your embedding/index field name.
query_model_string = 'meta-llama/Llama-3-8b-chat-hf' # model API string from Together.

def handler(event,context):
    """The lambda handler that will actually query the database and send a reply over Slack"""
    event = loads(event['body']) #convert plain text json to python dictionary

    # Query the database https://www.mongodb.com/docs/atlas/atlas-vector-search/vector-search-stage/
    message_embedding = together.embeddings.create(input=event['message'], model=embedding_model_string)
    
    search_results = mongo.Denhac_Wiki.Articles.aggregate([
      {
        "$vectorSearch": {
          "queryVector": message_embedding,
          "path": vector_database_field_name,
          "numCandidates": 45, # this should be 10-20x the limit
          "limit": 3, # the number of documents to return in the results
          "index": vector_database_field_name, # the index name you used in Step 4.
        } # https://docs.together.ai/docs/inference-models
      } # The largest articles have ~2100 tokens so an 8k context model should accurately interpret 3 articles + the user's query
    ])

    # BIG AI STUFF
    prompt = "You are a helpful digital assistant made to answer questions about the Denhac Hackerspace. "
    "Based on the user's query and relevant articles from the hackerspace wiki, provide the most complete, helpful, and concise answer possible. "
    "If the prompt pertains to Denhac's facilities but the answer is not contained in the wiki, do not try to guess the correct information about Denhac and instead inform the user that you do not know. "
    "<User's Query>\n" + event['message'] + "\n</User's Query>\n "
    "<Wiki Articles>\n" + "\n\n----------\n\n".join(["Title: " + article['title'] + "\n" + article['content'] for article in search_results]) + "</Wiki Articles>\n"
    
    response = together.Complete.create(
        prompt=prompt,
        model=query_model_string,
        # max_tokens = 512,
        # temperature = 0.8,
        # top_k = 60,
        # top_p = 0.6,
        # repetition_penalty = 1.1,
        # stop = stop_sequences
    )

    # Send the reply over slack
    ### send slack this: response["output"]["choices"][0]["text"]

    return "Big Success: " + response["output"]["choices"][0]["text"]
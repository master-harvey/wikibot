from pymongo import MongoClient
from json import loads
from botocore.vendored.requests import get
from datetime import datetime
from html.parser import HTMLParser
from openai import OpenAI
import os

# Takes the default mongo connection string but without the prepended user creds and has the token query parameter placed at the end
mongo = MongoClient(host=os.environ["MONGODB_URI"]+os.environ["AWS_SESSION_TOKEN"])
AI = OpenAI(api_key=os.environ["TOGETHER_API_KEY"], base_url='https://api.together.ai/v1')

embedding_model_string = 'togethercomputer/m2-bert-80M-8k-retrieval' # model API string from Together.
vector_database_field_name = 'embedding_together_m2-bert-8k-retrieval' # define your embedding/index field name.

#courtesy of https://stackoverflow.com/questions/14694482/converting-html-to-text-with-python
class HTMLFilter(HTMLParser):
    text = ""
    def handle_data(self, data):
        self.text += data

def handler(event,context):
    """This function will run regularly and will poll for updates to the wiki and update or add the embeddings"""
    # Request any updates from the last 24 hours (forbidden without a user agent)
    user_agent = "DenhacWikiBot/1.0 (+https://github.com/master-harvey/wiki-bot)"
    PAST_DAY = (datetime.datetime.now() - datetime.timedelta(days=8))
    with get(f"https://denhac.org/wp-json/wp/v2/epkb_post_type_1?modified_after={PAST_DAY.isoformat()}", headers={'User-Agent': user_agent}) as response:
        # Read the response data
        articles = loads(response.json())
        for article in articles:
            # Parse the article from article.content.rendered
            filter = HTMLFilter()
            filter.feed(article['content']['rendered'])
            content = filter.text

            # Check content length (no articles with 10 words or less)
            if content.count(' ') < 10:
                continue

            # Update embeddings for each updated post
            embeddings = AI.embeddings.create(input=content, model=embedding_model_string)

            # Store embeddings in mongodb
            mongo.Denhac_Wiki.Articles.update_one(
                {'_id': article['id']}, # Mirror wordpress' id field
                {'$set': {
                    [vector_database_field_name]: embeddings,
                    'title': article['title'],
                    'content': content,
                }},
                upsert=True  # Insert the document if it does not exist
            )

    return "Big Success"
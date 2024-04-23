from pymongo import MongoClient
from json import loads
from botocore.vendored import requests
from datetime import datetime
from html.parser import HTMLParser
from openai import OpenAI
import os

# Takes the default connection string provided in the 'Donnecting with MongoDB [python] Driver' wizard in the Atlas dashboard.
mongo = MongoClient(os.environ["MONGODB_URI"]
        .replace('<session token (for AWS IAM Roles)>',os.environ["AWS_SESSION_TOKEN"])
        .replace('<AWS access key>',os.environ["AWS_ACCESS_KEY_ID"])
        .replace('<AWS secret key>',os.environ["AWS_SECRET_ACCESS_KEY"]))

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
    PAST_WEEK = (datetime.datetime.now() - datetime.timedelta(days=7))
    with requests.get(f"https://denhac.org/wp-json/wp/v2/epkb_post_type_1?modified_after={PAST_WEEK.isoformat()}", headers={'User-Agent': user_agent}) as response:
        # Read the response data
        articles = loads(response.json())
        print("Response Loaded")
        for article in articles:
            # Parse the article from article.content.rendered
            filter = HTMLFilter()
            filter.feed(article['content']['rendered'])
            content = filter.text
            print("Rendered " + article['title'])

            # Check content length (no articles with 10 words or less)
            if content.count(' ') < 10:
                print("\t<insufficient content>")
                continue

            # Update embeddings for each updated post
            embeddings = AI.embeddings.create(input=content, model=embedding_model_string)
            print("Embeddings generated")

            # Store embeddings in mongodb
            mongo.Denhac_Wiki.Articles.update_one(
                {'_id': article['id']}, # Mirror wordpress' id field
                {'$set': {
                    [vector_database_field_name]: embeddings,
                    'title': article['title'],
                    'URL': article['link'],
                    'content': content,
                }},
                upsert=True  # Insert the document if it does not exist
            )

    return "Big Success"
from pymongo import MongoClient
from botocore.vendored import requests
from datetime import datetime
from openai import OpenAI
import urllib.parse
from bs4 import BeautifulSoup
import os

# Takes the default connection string provided in the 'Donnecting with MongoDB [python] Driver' wizard in the Atlas dashboard.
mongo = MongoClient(os.environ["MONGODB_URI"]
        .replace('<session token (for AWS IAM Roles)>',urllib.parse.quote_plus(os.environ["AWS_SESSION_TOKEN"]))
        .replace('<AWS access key>',urllib.parse.quote_plus(os.environ["AWS_ACCESS_KEY_ID"]))
        .replace('<AWS secret key>',urllib.parse.quote_plus(os.environ["AWS_SECRET_ACCESS_KEY"]))
        )

AI = OpenAI(api_key=os.environ["TOGETHER_API_KEY"], base_url='https://api.together.ai/v1')
embedding_model_string = 'togethercomputer/m2-bert-80M-8k-retrieval' # model API string from Together.
vector_database_field_name = 'embedding_together_m2-bert-8k-retrieval' # define your embedding/index field name.
user_agent = "DenhacWikiBot/1.0 (+https://github.com/master-harvey/wikibot)"

def handler(event,context):
    """This function will run regularly and will poll for updates to the wiki and update or add the embeddings"""
    # Request any updates from the last 24 hours (forbidden without a user agent) # TODO: published articles only and check for newly created articles, and check for deleted articles
    PAST_WEEK = (datetime.datetime.now() - datetime.timedelta(days=7))
    with requests.get(f"https://denhac.org/wp-json/wp/v2/epkb_post_type_1?modified_after={PAST_WEEK.isoformat()}", headers={'User-Agent': user_agent}) as response:
        # Read the response data
        articles = response.json()
        for article in articles:
            # Parse the article from article.content.rendered
            soup = BeautifulSoup(article['content']['rendered'])
            content = soup.get_text()
            print("Rendered " + article['title']['rendered'])

            # Check content length (no articles with 10 words or less)
            if content.count(' ') < 10:
                print("\t<insufficient content>")
                continue

            # Update embeddings for each updated post
            embeddings = AI.embeddings.create(input=content, model=embedding_model_string).data[0].embedding
            print("Embeddings generated")

            # Store embeddings in mongodb
            mongo.Denhac_Wiki.Articles.update_one(
                {'_id': article['id']}, # Mirror wordpress' id field
                {'$set': {
                    [vector_database_field_name]: embeddings,
                    'title': article['title']['rendered'],
                    'URL': article['link'],
                    'content': content,
                }},
                upsert=True  # Insert the document if it does not exist
            )

    return "Big Success"
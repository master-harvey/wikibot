from pymongo import MongoClient
from json import loads
from botocore.vendored.requests import get
from datetime import datetime
import together
import os

# Takes the default mongo connection string but without the prepended user creds and has the token query parameter placed at the end
mongo = MongoClient(host=os.environ["MONGODB_URI"]+os.environ["AWS_SESSION_TOKEN"])
together.api_key = os.environ["TOGETHER_API_KEY"]
together = together.Together()

embedding_model_string = 'togethercomputer/m2-bert-80M-8k-retrieval' # model API string from Together.
vector_database_field_name = 'embedding_together_m2-bert-8k-retrieval' # define your embedding field name.


def handler(event,context):
    """This function will run nightly and will poll for updates to the wiki and update or add the embeddings"""
    # Request updates
    PAST_DAY = (datetime.datetime.now() - datetime.timedelta(days=1))
    with get(f"https://denhac.org/wp-json/wp/v2/epkb_post_type_1?modified_after={PAST_DAY.isoformat()}") as response:
        # Read the response data
        articles = loads(response.json())
        for article in articles:
            # Parse the article from article.content.rendered

            # Shit-test each article to see if it even has content and what not

            # Update embeddings for each updated post that passes the shit-tests
            embeddings = together.embeddings.create(
                input=,
                model=,
            )

            db = mongo.

    return "Big Success"
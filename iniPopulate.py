from pymongo import MongoClient
import requests
from openai import OpenAI
import sys
from datetime import timedelta, datetime
from bs4 import BeautifulSoup
import time

# Takes the default connection string provided in the 'Connecting with MongoDB [python] Driver' wizard in the Atlas dashboard.
mongo = MongoClient(sys.argv[1].replace("<username>",sys.argv[2]).replace("<password>",sys.argv[3]))

AI = OpenAI(api_key=sys.argv[4], base_url='https://api.together.ai/v1')
embedding_model_string = 'togethercomputer/m2-bert-80M-8k-retrieval' # model API string from Together.
vector_database_field_name = 'embedding_together_m2-bert-8k-retrieval' # define your embedding/index field name.

def populate():
    """To be run once locally to initialize the database with all current articles"""
    # Request any updates from the last 24 hours (forbidden without a user agent)
    user_agent = "DenhacWikiBot/1.0 (+https://github.com/master-harvey/wikibot)"
    # Limited to 10 articles per request, step through a sliding window of 7 days to eventually retrieve all articles from 2021 to now
    startDate = datetime(month=1, day=1, year=2021)
    window    = timedelta(days=7)
    while startDate < datetime.now():
        with requests.get(f"https://denhac.org/wp-json/wp/v2/epkb_post_type_1?post_status=publish&modified_after={startDate.isoformat()}&modified_before={(startDate+window).isoformat()}", headers={'User-Agent': user_agent}) as response:
            # Read the response data
            articles = response.json()
            print(f"Response Loaded for {startDate.isoformat()} - {(startDate+window).isoformat()}",len(articles))
                
            for article in articles:
                # Parse the article from article.content.rendered
                soup = BeautifulSoup(article['content']['rendered'], features="html.parser")
                content = soup.get_text()
                print("Rendered: ", article['title']['rendered'])

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
                        str(vector_database_field_name): embeddings,
                        'title': article['title']['rendered'],
                        'URL': article['link'],
                        'content': content,
                    }},
                    upsert=True # Insert the document if it does not exist
                )
        time.sleep(30) # Sleep for 30 seconds to avoid hitting the rate limit
        startDate += window #step to the next week
    print( "Big Success" )
    return "Big Success"

if __name__ == "__main__":
    populate()
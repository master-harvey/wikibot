from json import loads
import os
from pymongo import MongoClient

client = MongoClient(host=os.environ["MONGODB_URI"])

def handler(event,context):
    """The lambda handler that will actually query the database and send a reply over Slack"""
    event = loads(event['body']) #convert plain text json to python dictionary

    # Query the database
    # BIG AI STUFF
    # Send the reply over slack

    return "Big Success"
from json import loads, dumps
import boto3
from os import environ

lambda_client = boto3.client('lambda')

def handler(event,context):
    """The lambda handler that will process 'events' (messages) from Slack [https://api.slack.com/apis/connections/events-api]. 
    This function will be deployed with a function URL that will serve as Slack's request endpoint. 
    Because slack requires 'a swift and confident HTTP 200' reponse from the server this function simply validates
     the event before passing everything to the generateReply function that oversees the inference and response to the user"""
    # print("EVENT: ",event," :EVENT")
    # print("CONTEXT: ",context," :CONTEXT")
    try:
        event = loads(event['body'])
    except:
        event = event['body'] #convert plain text json to python dictionary
        
    # Event validation (runs one time when the endpoint is added to Slack)
    if event['type'] == 'url_verification':
        return { "statusCode":200, "Content-type":"text/plain", "body":event['challenge'] }
    
    # If this isn't a message from the bot itself
    if event['event']['user'] != environ['SLACK_BOT_ID']:
        # Asynchronously invoke the generateReply lambda function
        lambda_client.invoke(
            FunctionName='WikiBot-GenerateReply',
            InvocationType='Event',  #Specifies asynchronous execution
            Payload=dumps({"body":event})
        )
        
        print("Big Success")
        
    return { "statusCode": 200 }
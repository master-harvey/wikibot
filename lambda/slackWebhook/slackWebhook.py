from json import loads
def handler(event,context):
    """The lambda handler that will process 'events' (messages) from Slack [https://api.slack.com/apis/connections/events-api]. 
    This function will be deployed with a function URL that will serve as Slack's request endpoint. 
    Because slack requires 'a swift and confident HTTP 200' reponse from the server this function simply validates
     the event before passing everything to the generateReply function that oversees the inference and response to the user"""
    print("EVENT: ",event," :EVENT")
    print("CONTEXT: ",context," :CONTEXT")
    event = loads(event['body']) #convert plain text json to python dictionary

    # Verify the event is a slack event, throw error on failure
    # TODO: Extract the X-Slack-Signature header and use it to verify this message came from Slack: https://api.slack.com/authentication/verifying-requests-from-slack

    # Event validation (runs one time when the endpoint is added to Slack)
    if event['type'] == 'url_verification':
        return { "statusCode":200, "Content-type":"text/plain", "body":event['challenge'] }
    
    # Trigger the generateReply lambda function

    return { "statusCode": 200 }